import wave
from pathlib import Path
from PIL import Image
import numpy as np
import logging

class CapacityError(Exception):
    """Custom exception for capacity-related errors"""
    pass

def check_audio_lsb_capacity(audio_path: str, payload_size: int) -> None:
    """
    Check if audio file has enough capacity for LSB embedding
    Raises CapacityError with detailed message if insufficient
    """
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.getnframes()
            sample_rate = audio.getframerate()
            duration = frames / sample_rate
            
        # Calculate overhead and requirements
        overhead_bits = len(b'###START######END###') * 8 + 256  # AES overhead estimate
        required_bits = (payload_size * 8) + overhead_bits
        available_bits = frames
        
        if required_bits > available_bits:
            # Calculate recommended audio size
            needed_frames = required_bits
            needed_duration = needed_frames / sample_rate
            needed_mb = (needed_frames * 2) / (1024 * 1024)  # 16-bit audio
            
            raise CapacityError(
                f"Audio file too small! Your {payload_size/1024:.1f}KB payload needs "
                f"{needed_duration:.1f}s of audio (≈{needed_mb:.1f}MB WAV file). "
                f"Current audio: {duration:.1f}s. Please use a longer audio file."
            )
            
        # Log success info
        utilization = (required_bits / available_bits) * 100
        logging.info(f"Audio capacity check passed. Utilization: {utilization:.1f}%")
        
    except wave.Error:
        raise CapacityError("Invalid audio file format")
    except Exception as e:
        logging.error(f"Error checking audio capacity: {e}")
        raise CapacityError(f"Could not analyze audio file: {str(e)}")

def check_image_lsb_capacity(image_path: str, payload_size: int) -> None:
    """
    Check if image has enough capacity for LSB embedding
    Raises CapacityError with detailed message if insufficient
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = width * height
            available_bits = pixels * 3  # 3 color channels
            
        # Calculate overhead and requirements  
        overhead_bits = len(b'###START######END###') * 8 + 32 + 256  # markers + length + AES
        required_bits = (payload_size * 8) + overhead_bits
        
        if required_bits > available_bits:
            # Calculate recommended image size
            needed_pixels = required_bits // 3
            needed_dimension = int(np.sqrt(needed_pixels))
            needed_mb = (needed_pixels * 3) / (1024 * 1024)  # RGB image
            
            raise CapacityError(
                f"Image too small! Your {payload_size/1024:.1f}KB payload needs "
                f"≈{needed_dimension}x{needed_dimension} pixel image (≈{needed_mb:.1f}MB). "
                f"Current image: {width}x{height}. Please use a larger image."
            )
            
        # Log success info
        utilization = (required_bits / available_bits) * 100
        logging.info(f"Image capacity check passed. Utilization: {utilization:.1f}%")
        
    except Exception as e:
        logging.error(f"Error checking image capacity: {e}")
        raise CapacityError(f"Could not analyze image file: {str(e)}")

def check_histogram_capacity(image_path: str) -> None:
    """
    Check if image meets minimum requirements for histogram shift (fixed ~150 bytes)
    Raises CapacityError if image is too small
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = width * height
            
        # Fixed payload for histogram: ~150 bytes = 1200 bits
        required_bits = 150 * 8  
        available_bits = pixels * 3
        
        # Minimum requirements: 20x20 image (400 pixels * 3 = 1200 bits)
        min_pixels = required_bits // 3
        min_dimension = int(np.sqrt(min_pixels))
        
        if pixels < min_pixels:
            raise CapacityError(
                f"Image too small for histogram method! "
                f"Minimum required: {min_dimension}x{min_dimension} pixels. "
                f"Current image: {width}x{height} pixels. "
                f"Please use an image of at least {min_dimension}x{min_dimension} pixels."
            )
            
        logging.info(f"Histogram capacity check passed. Image size: {width}x{height}")
        
    except Exception as e:
        logging.error(f"Error checking histogram capacity: {e}")
        raise CapacityError(f"Could not analyze image file: {str(e)}")

def check_phase_capacity(audio_path: str) -> None:
    """
    Check if audio meets minimum requirements for phase coding (fixed ~150 bytes)
    Raises CapacityError if audio is too short
    """
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.getnframes()
            sample_rate = audio.getframerate()
            duration = frames / sample_rate
            
        # Fixed payload for phase coding: ~150 bytes = 1200 bits
        required_bits = 150 * 8
        block_length = int(2 * 2 ** np.ceil(np.log2(2 * required_bits)))
        block_number = int(np.ceil(frames / block_length))
        
        B = 8  # bits per block
        available_capacity = block_number * B
        
        # Minimum requirements: ~3 seconds of audio at 44.1kHz
        min_blocks_needed = required_bits // B
        min_frames_needed = min_blocks_needed * block_length
        min_duration_needed = min_frames_needed / sample_rate
        
        if frames < min_frames_needed:
            raise CapacityError(
                f"Audio too short for phase coding method! "
                f"Minimum required: {min_duration_needed:.1f} seconds. "
                f"Current audio: {duration:.1f} seconds. "
                f"Please use audio of at least {min_duration_needed:.1f} seconds."
            )
            
        logging.info(f"Phase capacity check passed. Audio duration: {duration:.1f}s")
        
    except wave.Error:
        raise CapacityError("Invalid audio file format")
    except Exception as e:
        logging.error(f"Error checking phase capacity: {e}")
        raise CapacityError(f"Could not analyze audio file: {str(e)}")