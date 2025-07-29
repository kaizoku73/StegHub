from PIL import Image
import random
from crypto_algo.aes import *
import numpy as np

### To varify if the image is valid
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

def hist_embed(cover_path, payload, key):

    try:
        if not valid_img(cover_path):
            raise ValueError(f"{cover_path} is not a valid PNG image file.")

        with Image.open(cover_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')

        pixels = list(img.getdata())

        if not isinstance(payload, str):
            raise ValueError("Message must be a string.")
        
        if len(payload.strip()) == 0:
            raise ValueError("Message can not be empty!!")
    
        if len(payload) > 100:
            raise ValueError("The limit exceeds 100 characters")
        
        payload = payload.ljust(100).encode('utf-8')
        epayload = encryption(payload, key)

        starting = b'HISTOSTART'
        ending = b'HISTO_END!'

        data = starting + epayload + ending

        bits = ''.join(f'{byte:08b}' for byte in data)
        total_bits = len(bits)

        max_bits = len(pixels) * 3 ### 3 color channels per pixel
        if len(bits) > max_bits:
            raise ValueError('Payload too large to embed in cover image.')

        arr = np.array(img, dtype=np.uint8)
        height, width, channel = arr.shape

        flat = {ch: arr[..., i].flatten() for i , ch in enumerate(('R','G','B'))}

        peaks, zeros, shifts = {},{},{}
        total_capacity = 0
        for ch in ('R','G','B'):
            hist, faltu = np.histogram(flat[ch], bins=256, range=(0,255))

            u, z = find_peak(hist)
            peaks[ch], zeros[ch] = u, z
            shifts[ch] = 1 if z > u else -1 
            total_capacity += hist[u]
            
            if z > u:
                mask = (flat[ch] > u) & (flat[ch] < z)
                flat[ch][mask] += 1
            else:
                mask = (flat[ch] < u) & (flat[ch] > z)
                flat[ch][mask] -= 1

        if total_capacity < total_bits:
            raise ValueError(f"Insufficient capacity : {total_capacity}")
        
        bits_pr_ch = total_bits // 3
        remainder = total_bits % 3

        bits_distro = {}
        start_idx = 0
        for i , ch in enumerate(('R','G','B')):
            extra = 1 if i < remainder else 0
            end_idx = start_idx + bits_pr_ch + extra
            bits_distro[ch] = bits[start_idx:end_idx]
            start_idx = end_idx

        seed = to_seed(key)
        mage = random.Random(seed)

        for ch in ('R','G','B'):
            channel_bits = bits_distro[ch]
            if not channel_bits:
                continue

            positions = list(range(flat[ch].size))
            mage.shuffle(positions)

            u = peaks[ch]
            shift = shifts[ch]
            bit_idx = 0

            for pos in positions:
                if bit_idx >= len(channel_bits):
                    break
                if flat[ch][pos] == u:
                    if channel_bits[bit_idx] == '1':
                        flat[ch][pos] = u + shift
                    bit_idx += 1
            
        stego = np.stack([flat[ch] for ch in ('R','G','B')], axis = 1)
        stego = stego.reshape((height, width, 3)).astype(np.uint8)
        Image.fromarray(stego, 'RGB').save("encoded.png")
        print("Successfully embedded the payload in the encoded.png")
    except Exception as e:
        raise ValueError("Error : ", e)

