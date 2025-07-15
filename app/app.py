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

# Batasi ukuran file upload (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

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

@app.route("/health")
def health_check():
    """Health check endpoint untuk monitoring - lebih permisif untuk deployment."""
    try:
        # Basic health check yang tidak bergantung pada EasyOCR
        return jsonify({
            "status": "ok", 
            "message": "Service is running",
            "ready": True,
            "timestamp": time.time()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "ready": False
        }), 500

@app.route("/health/deep")
def deep_health_check():
    """Deep health check yang mengecek EasyOCR."""
    try:
        from app.ocr.ocr_engine import get_ocr_reader
        ocr_reader = get_ocr_reader()
        if ocr_reader is None:
            return jsonify({
                "status": "warning", 
                "message": "EasyOCR not initialized",
                "ready": False
            }), 503
        return jsonify({
            "status": "ok", 
            "message": "Service is fully healthy",
            "ready": True,
            "ocr_ready": True
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "ready": False
        }), 503

# --- Endpoint untuk Bukti Setor ---

@app.route('/api/bukti_setor/uploads/<path:filename>')
def serve_preview(filename):
    """Menyajikan file gambar preview yang telah disimpan."""
    upload_folder = app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

@app.route('/api/bukti_setor/process', methods=['POST'])
def process_bukti_setor_endpoint():
    """Endpoint utama untuk memproses file yang diunggah."""
    try:
        if 'file' not in request.files:
            return jsonify(error="File tidak ditemukan dalam permintaan"), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify(error="Tidak ada file yang dipilih"), 400
            
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify(error="Jenis file tidak didukung"), 400

        upload_folder = app.config['UPLOAD_FOLDER']
        # Buat nama file yang unik untuk menghindari konflik
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{uuid.uuid4()}_{int(time.time())}{file_extension}"
        filepath = os.path.join(upload_folder, safe_filename)
        
        # Simpan file dengan error handling
        try:
            file.save(filepath)
        except Exception as e:
            app.logger.error(f"Error saving file: {e}")
            return jsonify(error="Gagal menyimpan file"), 500

        try:
            poppler_path = app.config.get('POPPLER_PATH')
            # Panggil fungsi orkestrator dari processor.py
            extracted_data = extract_bukti_setor_data(filepath, poppler_path)
            return jsonify(message="Data berhasil diekstrak.", data=extracted_data), 200
        except ConnectionError as e:
            app.logger.error(f"OCR Connection Error: {e}")
            return jsonify(error="Service OCR tidak tersedia"), 503
        except Exception as e:
            app.logger.error(f"Error processing bukti setor: {e}\n{traceback.format_exc()}")
            return jsonify(error=f"Terjadi kesalahan di server: {str(e)}"), 500
        finally:
            # Selalu hapus file sementara setelah selesai diproses
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    app.logger.warning(f"Failed to remove temp file {filepath}: {e}")
                    
    except Exception as e:
        app.logger.error(f"Unexpected error in endpoint: {e}\n{traceback.format_exc()}")
        return jsonify(error="Terjadi kesalahan tidak terduga"), 500

# ==============================================================================
# Entry Point untuk Menjalankan Server
# ==============================================================================

if __name__ == "__main__":
    # Port diambil dari file .env, dengan default 8000
    port = int(os.environ.get("PORT", 8000))
    # Debug mode hanya untuk development
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    # 'host="0.0.0.0"' membuat server dapat diakses dari luar container Docker
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
