from PIL import Image
import random
from crypto_algo.aes import *
import numpy as np

def valid_img(cover_path):
    try:
        with Image.open(cover_path) as img:
            # Check format first
            if img.format and img.format.upper() == "PNG":
                img.verify()  # Only verify if it claims to be PNG
                return True
            return False
    except Exception:
        return False

def find_peak(hist):
    u = int(np.argmax(hist))
    zero_bins = np.where(hist == 0)[0]
    if zero_bins.size:
        z = zero_bins[np.argmin(np.abs(zero_bins - u))]
    else:
        z = int(np.argmin(hist))
    return u, z

def hist_extract(stego_path, key):
    try:
        if not valid_img(stego_path):
            raise ValueError(f"{stego_path} is not a valid PNG image file.")
        
        # Load image
        with Image.open(stego_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
        
            arr = np.array(img, dtype=np.uint8)
        height, width, channels = arr.shape
        flat = {ch: arr[..., i].flatten() for i, ch in enumerate(('R','G','B'))}
        
        # Analyze histograms
        peaks, zeros, shifts = {}, {}, {}
        total_capacity = 0
        
        for ch in ('R','G','B'):
            hist, _ = np.histogram(flat[ch], bins=256, range=(0,255))
            u, z = find_peak(hist)
            peaks[ch], zeros[ch] = u, z
            shifts[ch] = 1 if z > u else -1
            total_capacity += hist[u]
            
        
        total_bits = 152 * 8
        bits_pr_ch = total_bits // 3
        remainder = total_bits % 3
        
        seed = to_seed(key)
        rng = random.Random(seed)

        extracted_bits = []
        
        for i, ch in enumerate(('R','G','B')):
            extra = 1 if i < remainder else 0
            channel_bits_count = bits_pr_ch + extra

            # Same randomization as embedding
            positions = list(range(flat[ch].size))
            rng.shuffle(positions)
            
            u = peaks[ch]
            shift = shifts[ch]
            channel_bits = []
            
            for pos in positions:
                if len(channel_bits) >= channel_bits_count:
                    break
                
                pixel_value = flat[ch][pos]
                
                if pixel_value == u:
                    channel_bits.append('0')
                elif pixel_value == u + shift:
                    channel_bits.append('1')
            
            extracted_bits.extend(channel_bits)
        
        bit_string = ''.join(extracted_bits[:total_bits])
        byte_data = bytearray()
        
        for i in range(0, len(bit_string), 8):
            byte_chunk = bit_string[i:i+8]
            if len(byte_chunk) == 8:
                byte_data.append(int(byte_chunk, 2))
        
        
        starting = b'HISTOSTART'
        ending = b'HISTO_END!'
        
        if not byte_data.startswith(starting):
            raise ValueError("Start marker not found - wrong key or corrupted data")
        
        if not byte_data.endswith(ending):
            raise ValueError("End marker not found - extraction incomplete")
        
        encrypted_payload = bytes(byte_data[10:-10])
        
        # Decrypt
        decrypted_data = decryption(encrypted_payload, key)
        message = decrypted_data.decode('utf-8').rstrip()
        
        print(message)
        return message
        
    except Exception as e:
        raise ValueError(f"Extraction failed: {str(e)}")