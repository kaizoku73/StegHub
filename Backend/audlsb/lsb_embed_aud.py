import wave
import random
from crypto_algo.aes import *

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

def embed_lsb_aud(cover_path, payload_path, key):
    
    try:
        if not valid_wav(cover_path):
            raise ValueError(f"{cover_path} is not a valid WAV file")
        
        with wave.open(cover_path, mode='rb') as song:
            frame_bytes = bytearray(song.readframes(song.getnframes()))
            params = song.getparams()

        with open(payload_path, 'rb') as f:
            payload = f.read()

        payload = encryption(payload, key)

        starting = b'###START###'
        ending = b'###END###'
        full_payload = starting + payload + ending

        payload_bits = []
        for byte in full_payload:
            bits = format(byte, '08b')
            payload_bits.extend([int(b) for b in bits])

        #check if audio file has enough space to hold the payload
        max_payload_bits = len(frame_bytes)
        if len(payload_bits) > max_payload_bits:
            raise ValueError(f"Payload too large! Need {len(payload_bits)} bits but only have {max_payload_bits} available")

        seed = to_seed(key)
        shifu = random.Random(seed)
        indexes = list(range(len(frame_bytes)))
        shifu.shuffle(indexes)

        for bit_idx, bit in enumerate(payload_bits):
            i = indexes[bit_idx]
            frame_bytes[i] = (frame_bytes[i] & 0xFE) | bit

        output_path = "stego_file.wav"
        with wave.open(output_path, 'wb') as fd:
            fd.setparams(params)
            fd.writeframes(bytes(frame_bytes))

        return output_path
    
    except (ValueError, IOError, wave.Error) as e:
        print(f"Error in embed_audio: {e}")
        raise ValueError(f"Audio embedding failed: {str(e)}")