from pathlib import Path
import uvicorn

from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


from imglsb.lsb_embed_img import embed_lsb_img
from imglsb.lsb_extract_img import extract_lsb_img
from histogram.histo_embed import hist_embed
from histogram.histo_extract import hist_extract
from audlsb.lsb_embed_aud import embed_lsb_aud
from audlsb.lsb_extract_aud import extract_lsb_aud
from phase.phase_embed import embed_phase
from phase.phase_extract import extract_phase
from utils.capacity_check import *
from helper import *


import logging
logging.basicConfig(level=logging.INFO)

async def validate_file_size(file: UploadFile, max_size_mb: int, file_type: str = "file"):
    """
    Validate uploaded file size without loading entire file into memory
    """
    if not file:
        return
    
    # Reset file pointer to beginning
    await file.seek(0)
    
    # Read file in chunks to check size without loading all into memory
    total_size = 0
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    while True:
        chunk = await file.read(8192)  # Read 8KB chunks
        if not chunk:
            break
        total_size += len(chunk)
        
        if total_size > max_size_bytes:
            actual_size_mb = total_size / (1024*1024)
            raise HTTPException(
                status_code=413, 
                detail=f"{file_type.capitalize()} file too large! "
                      f"Maximum allowed size for {file_type} is {max_size_mb}MB. "
                      f"Your file is approximately {actual_size_mb:.1f}MB."
            )
    
    # Reset file pointer back to beginning for actual processing
    await file.seek(0)

app = FastAPI(
    title="Steghide API", 
    version="1.0.0",
    description="Advanced Steganography Tool with LSB, Histogram Shift, and Phase Coding"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://steghub.onrender.com","http://localhost:3000","http://127.0.0.1:3000","https://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 100 * 1024 * 1024:  # 100MB limit
            return JSONResponse(
                status_code=413,
                content={"detail": "File too large"}
            )
    response = await call_next(request)
    return response

# Temp directory setup
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Add OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {
        "message": "OK",
        "method": "OPTIONS",
        "path": full_path
    }

# Also add a specific OPTIONS handler for the embed endpoints
@app.options("/embed/{endpoint:path}")
async def embed_options_handler(endpoint: str):
    return {"message": "OK"}

@app.options("/extract/{endpoint:path}")
async def extract_options_handler(endpoint: str):
    return {"message": "OK"}



# ==================== IMAGE LSB ENDPOINTS ====================

@app.post("/embed/image/lsb")
async def embed_file_in_image_lsb(
    cover_image: UploadFile = File(...),
    secret_file: UploadFile = File(...),
    key: str = Form(...)
):
    """
    Hide a file inside an image using LSB method
    - Supports PNG Only
    - Key-based randomization for security
    - AES encryption
    - Max cover file size: 100MB
    - Max payload file size: 40MB
    """

    await validate_file_size(cover_image, 100, "cover image")
    await validate_file_size(secret_file, 40, "payload")

    cover_path = save_upload_file(cover_image, TEMP_DIR)
    secret_path = save_upload_file(secret_file, TEMP_DIR)
    
    with temp_file_manager(cover_path, secret_path):
        try:
            ### CHECK CAPACITY
            payload_size = Path(secret_path).stat().st_size
            check_image_lsb_capacity(cover_path, payload_size)
            
            embed_lsb_img(
                cover_path, secret_path, key
            )
            temp_stego = move_to_temp("steg_file.png", TEMP_DIR)
            
            if temp_stego:
                return FileResponse(
                    temp_stego, 
                    filename="stego_image.png",
                    media_type="image/png"
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to embed file in image")
        except CapacityError as e:
            raise HTTPException(status_code=404, detail=str(e))       
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

@app.post("/extract/image/lsb")
async def extract_file_from_image_lsb(
    stego_image: UploadFile = File(...),
    key: str = Form(...)
):
    """
    Extract hidden file from image using LSB method (ShadowBits)
    """
    stego_path = save_upload_file(stego_image, TEMP_DIR)
    
    with temp_file_manager(stego_path):
        try:
            success = extract_lsb_img(
                stego_path, key
            )
            
            if success:
                temp_extracted = move_to_temp(success, TEMP_DIR)
                if temp_extracted:
                    return FileResponse(
                        temp_extracted,
                        filename=temp_extracted.name
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to extract file from image")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
        finally:
            cleanup_steganography_outputs()


# ==================== IMAGE HISTOGRAM ENDPOINTS ====================

@app.post("/embed/image/histogram")
async def embed_message_in_image_histogram(
    cover_image: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...)
):
    """
    Hide a text message (max 100 chars) in image using Histogram Shift
    - Max cover image size: 100MB
    """

    await validate_file_size(cover_image, 100, "cover image")

    if len(message) > 100:
        raise HTTPException(status_code=400, detail="Message too long. Maximum 100 characters allowed.")
    
    cover_path = save_upload_file(cover_image, TEMP_DIR)
    
    with temp_file_manager(cover_path):
        try:
            ### Check capacity
            check_histogram_capacity(cover_path)

            hist_embed(
                cover_path, message, key
            )
            temp_encoded = move_to_temp("encoded.png", TEMP_DIR)
            
            if temp_encoded:
                return FileResponse(
                    temp_encoded,
                    filename="histogram_stego.png",
                    media_type="image/png"
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to embed message using histogram shift")
        except CapacityError as e:
            raise HTTPException(status_code=404, detail=str(e))       
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Histogram embedding error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

@app.post("/extract/image/histogram")
async def extract_message_from_image_histogram(
    stego_image: UploadFile = File(...),
    key: str = Form(...)
):
    """
    Extract hidden message from image using Histogram Shift
    """
    stego_path = save_upload_file(stego_image, TEMP_DIR)
    
    with temp_file_manager(stego_path):
        try:
            extracted_message = hist_extract(
                stego_path,key
            )
            
            if extracted_message:
                return {"message": extracted_message}
            else:
                raise HTTPException(status_code=400, detail="Failed to extract message from image")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Histogram extraction error: {str(e)}")
        finally:
            cleanup_steganography_outputs()


# ==================== AUDIO LSB ENDPOINTS ====================

@app.post("/embed/audio/lsb")
async def embed_file_in_audio_lsb(
    cover_audio: UploadFile = File(...),
    secret_file: UploadFile = File(...),
    key: str = Form(...),
):
    """
    Hide a file inside audio using LSB method (ShadowBits)
    - Supports WAV ONLY
    - Key-based randomization
    - AES encryption
    - Max cover audio size: 100MB
    - Max payload file size: 40MB
    """

    await validate_file_size(cover_audio, 100, "cover audio")
    await validate_file_size(secret_file, 40, "payload")

    cover_path = save_upload_file(cover_audio, TEMP_DIR)
    secret_path = save_upload_file(secret_file, TEMP_DIR)
    
    with temp_file_manager(cover_path, secret_path):
        try:
            logging.info("Validating and converting audio format if needed...")
            wav_path = ensure_wav_format(cover_path, TEMP_DIR)
            if wav_path != cover_path:
                register_temp_file(wav_path)

            ### Capacity check
            payload_size = Path(secret_path).stat().st_size
            check_audio_lsb_capacity(wav_path, payload_size)

            logging.info("Starting LSB embeeding process...")
            success = embed_lsb_aud(
                wav_path, secret_path, key
            )
            
            if success:
                logging.info("LSB embedding completed successfully.")
                temp_stego = move_to_temp(success, TEMP_DIR)
                if temp_stego:
                    return FileResponse(
                        temp_stego,
                        filename="stego_audio.wav",
                        media_type="audio/wav"
                    )
            else:
                raise HTTPException(status_code=400, detail="Failed to embed file in audio")
        except CapacityError as e:
            raise HTTPException(status_code=404, detail=str(e))        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio embedding error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

@app.post("/extract/audio/lsb")
async def extract_file_from_audio_lsb(
    stego_audio: UploadFile = File(...),
    key: str = Form(...),
):
    """
    Extract hidden file from audio using LSB method (ShadowBits)
    """
    stego_path = save_upload_file(stego_audio, TEMP_DIR)
    
    with temp_file_manager(stego_path):
        try:
            payload = extract_lsb_aud(
                stego_path, key
            )
            
            if payload:
                possible_extensions = ['txt', 'pdf', 'jpg', 'jpeg', 'png', 'mp3', 'wav', 'doc', 'docx', 'zip', 'py']
                extracted_file = find_file("stego_file", possible_extensions)

                if extracted_file:
                    temp_extracted = move_to_temp(str(extracted_file), TEMP_DIR)

                    if temp_extracted:
                        return FileResponse(
                            temp_extracted,
                            filename=temp_extracted.name
                        )
            else:
                raise HTTPException(status_code=400, detail="Failed to extract file from audio")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio extraction error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

# ==================== AUDIO PHASE CODING ENDPOINTS ====================

@app.post("/embed/audio/phase")
async def embed_message_in_audio_phase(
    cover_audio: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...)
):
    """
    Hide a text message (max 100 chars) in audio using Phase Coding (ShadowPhase)
    - Uses FFT phase manipulation
    - AES-256 encrypted messages
    - Key-based frequency bin selection
    - Max cover audio size: 100MB
    """

    await validate_file_size(cover_audio, 100, "cover audio")

    if len(message) > 100:
        raise HTTPException(status_code=400, detail="Message too long. Maximum 100 characters allowed.")
    
    cover_path = save_upload_file(cover_audio, TEMP_DIR)
    
    with temp_file_manager(cover_path):
        try:
            wav_path = ensure_wav_format(cover_path, TEMP_DIR)
            if wav_path != cover_path:
                register_temp_file(wav_path)

            ### check capacity
            check_phase_capacity(wav_path)

            logging.info("Starting phase coding embedding...")
            result = embed_phase(
                wav_path, message, key
            )
            
            if result:
                logging.info("Embedding data using phase coding method completed.")
                temp_encoded = move_to_temp(result, TEMP_DIR)
                if temp_encoded:
                    return FileResponse(
                        temp_encoded,
                        filename="phase_stego.wav",
                        media_type="audio/wav"
                    )
            else:
                raise HTTPException(status_code=400, detail="Failed to embed message using phase coding")
        except CapacityError as e:
            raise HTTPException(status_code=404, detail=str(e))         
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Phase coding embedding error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

@app.post("/extract/audio/phase")
async def extract_message_from_audio_phase(
    stego_audio: UploadFile = File(...),
    key: str = Form(...)
):
    """
    Extract hidden message from audio using Phase Coding (ShadowPhase)
    """
    stego_path = save_upload_file(stego_audio, TEMP_DIR)
    
    with temp_file_manager(stego_path):
        try:
            logging.info("Extracting message from audio file...")
            extracted_message = extract_phase(
                stego_path, key
            )
            
            if extracted_message:
                logging.info("Successfully extracted the message from file.")
                return {"message": extracted_message}
            else:
                raise HTTPException(status_code=400, detail="Failed to extract message from audio")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Phase coding extraction error: {str(e)}")
        finally:
            cleanup_steganography_outputs()

# ==================== UTILITY ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint with auto cleanup"""
    # Auto cleanup when user visits/refreshes the page
    try:
        files_before = get_temp_files_count()
        cleanup_all_temp_files()
        cleanup_steganography_outputs()
        files_after = get_temp_files_count()
        
        cleanup_info = {
            "files_cleaned": files_before - files_after,
            "remaining_files": files_after
        }
    except Exception as e:
        cleanup_info = {"cleanup_error": str(e)}
    
    return {
        "message": "Steghide API is running", 
        "version": "1.0.0",
        "auto_cleanup": cleanup_info
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "temp_dir": str(TEMP_DIR),
        "tracked_files": get_temp_files_count()
    }

@app.get("/cleanup")
async def manual_cleanup():
    """Manual cleanup endpoint for testing"""
    files_before = get_temp_files_count()
    cleanup_all_temp_files()
    cleanup_steganography_outputs()
    files_after = get_temp_files_count()
    
    return {
        "message": "Cleanup completed", 
        "files_cleaned": files_before - files_after,
        "remaining_files": files_after
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)