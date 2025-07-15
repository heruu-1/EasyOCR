# File: config.py

import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
    """Konfigurasi utama aplikasi Flask."""

    # Pengaturan folder upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # Pengaturan ekstensi file yang diizinkan
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png").split(",")
    
    # Path Tesseract OCR (untuk Windows/Railway)
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
    
    # Path Poppler (untuk konversi PDF)
    POPPLER_PATH = os.getenv("POPPLER_PATH")
    
    # Secret key untuk Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Max file size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
