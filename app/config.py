import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

class Config:
    """
    Class Konfigurasi Utama (Stateless).
    """

    # --- Konfigurasi Path Eksternal ---
    # Mengambil path ke instalasi Poppler, yang dibutuhkan oleh pdf2image.
    POPPLER_PATH = os.getenv("POPPLER_PATH")

    # --- Konfigurasi File Upload ---
    # Menentukan nama folder untuk menyimpan file yang diunggah sementara.
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # Mengambil daftar ekstensi file yang diizinkan dari .env.
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png").split(","))