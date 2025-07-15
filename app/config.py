import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

class Config:
    """
    Class Konfigurasi Utama dengan optimasi production.
    """

    # --- Konfigurasi Path Eksternal ---
    POPPLER_PATH = os.getenv("POPPLER_PATH", "/usr/bin")

    # --- Konfigurasi File Upload ---
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    
    # Ekstensi file yang diizinkan
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png").split(","))
    
    # --- Performance Settings ---
    MAX_PAGES_PER_PDF = int(os.getenv("MAX_PAGES_PER_PDF", "10"))
    OCR_DPI = int(os.getenv("OCR_DPI", "150"))
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "800"))
    
    # --- Logging Settings ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # --- Security Settings ---
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
    
    # --- CORS Settings ---
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # --- Environment Detection ---
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"