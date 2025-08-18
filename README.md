# 🔐 Steghub - Advanced Steganography Tool

![Steghub Banner](https://img.shields.io/badge/Steghub-Advanced%20Steganography-00ff41?style=for-the-badge&logo=shield&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009639?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)


**Steghub** is a steganography platform that enables secure data hiding using multiple advanced techniques. Built with a modern FastAPI backend and a sleek cyberpunk-themed frontend, Steghub supports both image and audio steganography with military-grade AES encryption.

## ⚠️IMPORTANT
- **This project is only to use in local server as I have created this as my college's major project. Do not try to deploy this project as it was not meant for deployment, I have not added mostly technical specification for deployment. There's a reason as for why there is no platform for steganography on web that anyone(including criminals) would be able to use it and each operation takes usage of about 4-8GB RAM, so it will also be costly for you to host**

## ⚠️Disclaimer
- **This concept can be applied for both ethical and unethical purposes. The content of this project is for educational purposes only and is not to be used to play pranks, or harm people and infrastructure. Misuse of data hiding techniques for illegal or unethical activities may lead to serious legal consequences.**

## 🌟 Features

### 🖼️ **Image Steganography**
- **LSB (Least Significant Bit)**: Hide files of any type inside PNG images
- **Histogram Shifting**: Embed text messages using advanced histogram manipulation
- **AES-256 Encryption**: All embedded data is encrypted with user-defined keys
- **Key-based Randomization**: Pseudorandom pixel/bit selection for enhanced security

### 🎵 **Audio Steganography**
- **LSB Audio**: Hide files inside WAV audio with imperceptible quality loss
- **Phase Coding**: Embed text messages using FFT phase manipulation
- **Multi-format Support**: Automatic conversion from MP3, FLAC, M4A to WAV
- **Channel Selection**: Intelligent mono/stereo channel handling

### 🛡️ **Security Features**
- **AES-256-EAX Encryption**: Military-grade encryption for all payloads
- **Key Derivation**: SHA-256 based key derivation from user passwords
- **Data Integrity**: CRC32 checksums for corruption detection
- **Secure Markers**: Custom start/end markers for payload identification

### 🌐 **Web Interface**
- **Modern UI**: Cyberpunk-themed responsive interface
- **Real-time Processing**: Live file upload and processing feedback
- **Multi-method Support**: Switch between different steganography techniques
- **Download Integration**: Automatic file download after processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kaizoku73/steghub.git
cd steghub
```

2. **Set up the backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the backend server**
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Open the frontend**
```bash
cd ../frontend
# Open index.html in your browser or serve with a local server
python -m http.server 3000
```

5. **Access the application**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## 📖 Usage Guide

### Image LSB Steganography

**Embedding:**
```python
# Via API endpoint: POST /embed/image/lsb
# Files: cover_image (PNG), secret_file (any), key (string)
```

**Extracting:**
```python
# Via API endpoint: POST /extract/image/lsb  
# Files: stego_image (PNG), key (string)
```

### Histogram Shifting

**Embedding:**
```python
# Via API endpoint: POST /embed/image/histogram
# Files: cover_image (PNG), message (max 100 chars), key (string)
```

**Extracting:**
```python
# Via API endpoint: POST /extract/image/histogram
# Files: stego_image (PNG), key (string)
```

### Audio LSB Steganography

**Embedding:**
```python
# Via API endpoint: POST /embed/audio/lsb
# Files: cover_audio (WAV/MP3/FLAC), secret_file (any), key (string)
```

**Extracting:**
```python
# Via API endpoint: POST /extract/audio/lsb
# Files: stego_audio (WAV), key (string)
```

### Phase Coding

**Embedding:**
```python
# Via API endpoint: POST /embed/audio/phase
# Files: cover_audio (WAV), message (max 100 chars), key (string)
```

**Extracting:**
```python
# Via API endpoint: POST /extract/audio/phase
# Files: stego_audio (WAV), key (string)
```

## 🏗️ Architecture

### Backend Structure
```
backend/
├── main.py                 # FastAPI application and endpoints
├── requirements.txt        # Python dependencies
├── helper.py              # Utility functions and file management
├── audlsb/                # Audio LSB steganography
│   ├── lsb_embed_aud.py
│   └── lsb_extract_aud.py
├── crypto_algo/           # Encryption/decryption
│   └── aes.py
├── histogram/             # Histogram shifting
│   ├── histo_embed.py
│   └── histo_extract.py
├── imglsb/               # Image LSB steganography
│   ├── lsb_embed_img.py
│   └── lsb_extract_img.py
├── phase/                # Phase coding
│   ├── phase_embed.py
│   └── phase_extract.py
└── utils/                # Utilities
    ├── capacity_check.py
    └── validator.py
```

### Frontend Structure
```
frontend/
├── index.html            # Main HTML structure
├── style.css             # Cyberpunk-themed styling
└── main.js              # Application logic and API integration
```

## 🔧 API Endpoints

### Image Steganography
- `POST /embed/image/lsb` - Embed file in image using LSB
- `POST /extract/image/lsb` - Extract file from LSB image
- `POST /embed/image/histogram` - Embed message using histogram shifting
- `POST /extract/image/histogram` - Extract message from histogram image

### Audio Steganography  
- `POST /embed/audio/lsb` - Embed file in audio using LSB
- `POST /extract/audio/lsb` - Extract file from LSB audio
- `POST /embed/audio/phase` - Embed message using phase coding
- `POST /extract/audio/phase` - Extract message from phase audio

## 🎯 Technical Specifications

### Supported Formats

**Images:**
- Input: PNG (required for processing)
- Output: PNG (steganographic images)

**Audio:**
- Input: WAV, MP3, FLAC, M4A (auto-converted to WAV)
- Output: WAV (steganographic audio)

### Encryption Details
- **Algorithm**: AES-256 in EAX mode
- **Key Derivation**: SHA-256 hash of user password
- **Nonce**: 16 bytes (automatically generated)
- **Authentication**: Built-in authentication tag

## 🛠️ Development

### Code Style
- **Backend**: Follow PEP 8 standards
- **Frontend**: ES6+ JavaScript standards
- **Documentation**: Comprehensive docstrings and comments

## ⚠️ Security Considerations

### Data Security
- All temporary files are automatically cleaned up
- No persistent storage of user data
- Memory-based file processing when possible
- Secure random number generation for bit positioning

### Best Practices
- Use strong, unique keys for each operation
- Verify file integrity after extraction
- Keep payload sizes reasonable for better performance
- Use HTTPS in production environments

## 📊 Performance Metrics

### Typical Processing Times
- **Small Image LSB** (1MB image, 100KB payload): ~2-5 seconds
- **Large Image LSB** (10MB image, 1MB payload): ~10-20 seconds
- **Audio LSB** (3min audio, 500KB payload): ~5-15 seconds
- **Phase Coding** (3min audio, text message): ~8-25 seconds
- **Histogram** (5MB image, text message): ~3-8 seconds

### Resource Usage
- **Memory**: 2-4x the size of input files during processing
- **CPU**: Intensive during FFT operations (phase coding)
- **Storage**: Temporary files cleaned automatically

## 📜 License

This project is open source, feel free to use and modify it. Just don't forget to credit me if you share it!

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **Pillow**: For image processing capabilities  
- **NumPy/SciPy**: For numerical computing
- **Librosa**: For audio analysis
- **PyCryptodome**: For encryption implementations

---

**Built with ❤️ for privacy and security by kaizoku**

