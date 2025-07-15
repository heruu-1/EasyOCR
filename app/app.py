# File: app/app.py
# Deskripsi: Versi stateless dari entry point utama.
# Fokus murni pada pemrosesan file dan pengembalian data JSON, tanpa interaksi database.

# --- 1. Impor Pustaka Standar & Pihak Ketiga ---
import os
import uuid
import time
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# --- 2. Impor Modul Lokal ---
from app.config import Config
from app.ocr.processor import extract_bukti_setor_data
from app.utils.helpers import allowed_file

# ==============================================================================
# Inisialisasi Aplikasi Flask & Ekstensi
# ==============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi CORS untuk mengizinkan permintaan dari frontend
CORS(app, origins=[
    "http://localhost:3000",
    "https://proyek-pajak.vercel.app",
    os.environ.get("FRONTEND_URL")
], supports_credentials=True)

# Membuat folder upload jika belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# ==============================================================================
# Definisi Endpoint API (Routes)
# ==============================================================================

@app.route("/")
def index():
    """Endpoint dasar untuk memeriksa apakah server berjalan."""
    return "Hello from EasyOCR Stateless API!"

# --- Endpoint untuk Bukti Setor ---

@app.route('/api/bukti_setor/uploads/<path:filename>')
def serve_preview(filename):
    """Menyajikan file gambar preview yang telah disimpan."""
    upload_folder = app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

@app.route('/api/bukti_setor/process', methods=['POST'])
def process_bukti_setor_endpoint():
    """Endpoint utama untuk memproses file yang diunggah."""
    if 'file' not in request.files:
        return jsonify(error="File tidak ditemukan dalam permintaan"), 400

    file = request.files['file']
    if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        return jsonify(error="Jenis file tidak didukung"), 400

    upload_folder = app.config['UPLOAD_FOLDER']
    # Buat nama file yang unik untuk menghindari konflik
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}_{int(time.time())}{file_extension}"
    filepath = os.path.join(upload_folder, safe_filename)
    file.save(filepath)

    try:
        poppler_path = app.config.get('POPPLER_PATH')
        # Panggil fungsi orkestrator dari processor.py
        extracted_data = extract_bukti_setor_data(filepath, poppler_path)
        return jsonify(message="Data berhasil diekstrak.", data=extracted_data), 200
    except Exception as e:
        app.logger.error(f"Error processing bukti setor: {e}\n{traceback.format_exc()}")
        return jsonify(error=f"Terjadi kesalahan di server: {str(e)}"), 500
    finally:
        # Selalu hapus file sementara setelah selesai diproses
        if os.path.exists(filepath):
            os.remove(filepath)

# ==============================================================================
# Entry Point untuk Menjalankan Server
# ==============================================================================

if __name__ == "__main__":
    # Port diambil dari file .env, dengan default 5000
    port = int(os.environ.get("PORT", 8000))
    # 'host="0.0.0.0"' membuat server dapat diakses dari luar container Docker
    app.run(host="0.0.0.0", port=port, debug=True)
