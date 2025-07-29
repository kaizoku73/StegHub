"""
File management utilities for steganography API
Handles temporary file creation, cleanup, and audio conversion
"""

import uuid
from pathlib import Path
import time
import logging
import atexit
from contextlib import contextmanager
from typing import Set, Optional
import gc
from pydub import AudioSegment
from fastapi import UploadFile

# Global set to track temporary files
_temp_files: Set[str] = set()

def register_temp_file(file_path: str):
    """Register a temporary file for cleanup"""
    if file_path:
        _temp_files.add(str(file_path))

def unregister_temp_file(file_path: str):
    """Unregister a temporary file from cleanup"""
    if file_path:
        _temp_files.discard(str(file_path))

def cleanup_all_temp_files():
    """Cleanup all registered temporary files"""
    for file_path in list(_temp_files):
        cleanup_file(file_path)
    _temp_files.clear()

# Register cleanup on exit
atexit.register(cleanup_all_temp_files)

def force_close_file_handles():
    """Force garbage collection to close any open file handles"""
    gc.collect()
    time.sleep(0.1)

def cleanup_file(file_path: str, max_retries: int = 5, delay: float = 0.2) -> bool:
    """
    Safely delete a file with enhanced retry mechanism
    Returns True if successful, False otherwise
    """
    if not file_path:
        return True
    
    path = Path(file_path)
    
    if not path.exists():
        logging.info(f"File {file_path} does not exist, skipping cleanup")
        unregister_temp_file(file_path)
        return True
    
    # Force close any open file handles
    force_close_file_handles()
    
    for attempt in range(max_retries):
        try:
            # Try to make file writable if it's read-only
            if path.exists():
                path.chmod(0o666)
            
            path.unlink()
            logging.info(f"Successfully deleted: {file_path}")
            unregister_temp_file(file_path)
            return True
            
        except PermissionError as e:
            logging.warning(f"Permission denied deleting {file_path}, attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                force_close_file_handles()
                time.sleep(delay * (attempt + 1))
            else:
                logging.error(f"Failed to delete {file_path} after {max_retries} attempts: Permission denied")
                
        except FileNotFoundError:
            logging.info(f"File {file_path} already deleted")
            unregister_temp_file(file_path)
            return True
            
        except Exception as e:
            logging.warning(f"Error deleting {file_path}, attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                force_close_file_handles()
                time.sleep(delay * (attempt + 1))
            else:
                logging.error(f"Failed to delete {file_path} after {max_retries} attempts: {str(e)}")
    
    return False

@contextmanager
def temp_file_manager(*file_paths):
    """Context manager for automatic cleanup of temporary files"""
    try:
        for path in file_paths:
            if path:
                register_temp_file(path)
        yield
    finally:
        for path in file_paths:
            if path:
                cleanup_file(path)

def save_upload_file(upload_file: UploadFile, temp_dir: Path) -> str:
    """Save uploaded file to temp directory with automatic registration"""
    file_id = str(uuid.uuid4())
    file_path = temp_dir / f"{file_id}_{upload_file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            upload_file.file.seek(0)
            while chunk := upload_file.file.read(8192):
                buffer.write(chunk)
    finally:
        # Explicitly close the upload file
        if hasattr(upload_file.file, 'close'):
            upload_file.file.close()
    
    register_temp_file(str(file_path))
    return str(file_path)

def cleanup_steganography_outputs():
    """Clean up common steganography output files that might be left behind"""
    common_outputs = [
        "steg_file.png", "steg_file.wav", "encoded.png", "encoded.wav", 
        "extracted_file.txt", "extracted_file.pdf", "extracted_file.jpg",
        "extracted_file.png", "extracted_file.mp3", "extracted_file.wav",
        "stego_file.txt", "stego_file.pdf", "stego_file.jpg", "stego_file.png",
        "stego_file.zip", "stego_file.py", "stego_file.doc", "stego_file.docx"
    ]
    
    for filename in common_outputs:
        file_path = Path(filename)
        if file_path.exists():
            try:
                cleanup_file(str(file_path))
                logging.info(f"Cleaned up leftover file: {filename}")
            except Exception as e:
                logging.warning(f"Failed to clean {filename}: {e}")

def move_to_temp(source_name: str, temp_dir: Path) -> Optional[Path]:
    """Move file to temp directory with proper cleanup"""
    source = Path(source_name)
    if not source.exists():
        cleanup_steganography_outputs()
        return None
    
    dest = temp_dir / f"{uuid.uuid4()}_{source.name}"
    
    try:
        with open(source, 'rb') as src:
            with open(dest, 'wb') as dst:
                while chunk := src.read(8192):
                    dst.write(chunk)
        
        # Clean up source file
        cleanup_file(str(source))
        register_temp_file(str(dest))
        return dest
        
    except Exception as e:
        logging.error(f"Failed to move {source} to {dest}: {e}")
        cleanup_file(str(dest))
        return None

def find_file(base_name: str, extensions: list) -> Optional[Path]:
    """Find file with given base name and possible extensions"""
    for ext in extensions:
        file_path = Path(f"{base_name}.{ext}")
        if file_path.exists():
            return file_path
    return None

def ensure_wav_format(file_path: str, temp_dir: Path) -> str:
    """
    Convert audio file to WAV if it's not already WAV
    Returns path to WAV file (either original or converted)
    """
    if file_path.lower().endswith('.wav'):
        return file_path  
    
    logging.info(f"Audio file is not in wav format, converting to wav...")
    try:
        audio = AudioSegment.from_file(file_path)
        
        logging.info("Applying standard audio settings (44.1kHz, 16-bit, stereo)")
        audio = audio.set_frame_rate(44100)
        audio = audio.set_sample_width(2)  # 16-bit
        audio = audio.set_channels(2)      # Stereo
        
        # Create WAV file in temp directory
        file_id = str(uuid.uuid4())
        wav_path = temp_dir / f"{file_id}_converted.wav"
        
        audio.export(str(wav_path), format="wav")
        
        # Close audio object and force cleanup
        del audio
        force_close_file_handles()
        
        register_temp_file(str(wav_path))
        logging.info("Audio conversion completed successfully.")
        return str(wav_path)
        
    except Exception as e:
        logging.error(f"Audio conversion failed: {str(e)}")
        raise ValueError(f"Could not convert {file_path} to WAV: {str(e)}")

def get_temp_files_count() -> int:
    """Get count of tracked temporary files"""
    return len(_temp_files)

def get_temp_files_list() -> list:
    """Get list of tracked temporary files"""
    return list(_temp_files)