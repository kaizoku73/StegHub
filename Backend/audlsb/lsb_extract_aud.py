import wave
from crypto_algo.aes import *
import random
from utils.validator import detect_file_type

def valid_wav(cover_path):
    try:
        with wave.open(cover_path, 'rb') as wave_file:
            # Get WAV file properties
            channels = wave_file.getnchannels()
            sample_width = wave_file.getsampwidth()
            framerate = wave_file.getframerate()
            frames = wave_file.getnframes()
            
            # Validate parameters are within reasonable ranges
            if not (1 <= channels <= 8):  # Typical channel range
                return False
            if sample_width not in [1, 2, 3, 4]:  # Valid sample widths
                return False
            if not (8000 <= framerate <= 192000):  # Common sample rates
                return False
            if frames <= 0:
                return False
            
            # Try to read a small portion of audio data
            wave_file.readframes(min(1024, frames))
            
            return True
            
    except (wave.Error, EOFError, FileNotFoundError, PermissionError):
        return False
    except Exception:
        return False

def extract_lsb_aud(stego_path, key):

    try:
        if not valid_wav(stego_path):
            raise ValueError(f"{stego_path} is not a valid wav file")
        
        with wave.open(stego_path, 'rb') as song:
            frame_bytes = song.readframes(song.getnframes())

        ### Extracts Last bits of randomized byte
        seed = to_seed(key)
        shifu = random.Random(seed)
        indexes = list(range(len(frame_bytes)))
        shifu.shuffle(indexes)

        extracted_bits = []
        for i in indexes:
            extracted_bits.append(frame_bytes[i] & 1)

        ### convert bits back to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 7 < len(extracted_bits):
                byte_bits = extracted_bits[i:i+8]
                byte_value = 0
                for j, bit in enumerate(byte_bits):
                    byte_value |= bit << (7-j)
                extracted_bytes.append(byte_value)

        ### find starting and ending of the embedded payload
        starting = b'###START###'
        ending = b'###END###'

        try:
            start_byte = extracted_bytes.find(starting)
            if start_byte == -1:
                raise ValueError("Starting point not found - file may not contain embedded data or key is incorrect")
            
            search = start_byte + len(starting)
            end_byte = extracted_bytes.find(ending, search)
            if end_byte == -1:
                raise ValueError("Ending point not found - embedded data maybe corrupted")
            
            payload = bytes(extracted_bytes[search:end_byte])

        except Exception as e:
            print(f"Error finding hidden data : {e}")
            return None
        
        ### Decrypt if provided encryption duting embedding
        payload = decryption(payload, key)

        extension, mime_type = detect_file_type(payload)

        output_path = f"stego_file.{extension}"

        ### save the payload
        with open(output_path, 'wb') as fd:
            fd.write(payload)

        return payload
    
    except Exception as e:
        print(f"Error in extracting data from file: {e}")
        return None