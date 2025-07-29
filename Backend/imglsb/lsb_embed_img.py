from PIL import Image
import random
from crypto_algo.aes import *

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

def embed_lsb_img(cover_path, payload_path, key):

    try:
        if not valid_img(cover_path):
            raise ValueError(f"{cover_path} is not a valid PNG image file.")

        img = Image.open(cover_path)
        mode = img.mode

        if mode != 'RGB':
            img = img.convert('RGB')

        pixels = list(img.getdata())

        with open(payload_path, 'rb') as f:
            payload = f.read()

        payload = encryption(payload, key)

        starting = b'###START###'
        ending = b'###END###'

        length = len(payload).to_bytes(4, 'big')
        data = starting + length + payload + ending

        bits = ''.join(f'{byte:08b}' for byte in data)

        max_bits = len(pixels) * 3 ### 3 color channels per pixel
        if len(bits) > max_bits:
            raise ValueError('Payload too large to embed in cover image.')

        seed = to_seed(key)
        prng = random.Random(seed)
        indexes = list(range(len(pixels)))
        prng.shuffle(indexes)

        new_pixels = [None] * len(pixels)  
        bit_idx = 0
        
        for i in range(len(indexes)):
            pixel_idx = indexes[i]  
            r, g, b = pixels[pixel_idx]
        
            if bit_idx < len(bits):
                r = (r & ~1) | int(bits[bit_idx])
                bit_idx += 1
            if bit_idx < len(bits):
                g = (g & ~1) | int(bits[bit_idx])
                bit_idx += 1
            if bit_idx < len(bits):
                b = (b & ~1) | int(bits[bit_idx])
                bit_idx += 1

            new_pixels[pixel_idx] = (r, g, b)


        img.putdata(new_pixels)
        file = img.save("steg_file.png")

        return file
    except Exception as e:
        print(f"Error in embedding : {e}")
        raise