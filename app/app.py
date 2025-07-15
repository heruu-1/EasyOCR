# File: app/app.py
# Deskripsi: Versi stateless dari entry point utama.
# Fokus murni pada pemrosesan file dan pengembalian data JSON, tanpa interaksi database.

import os
import uuid
import time
import traceback
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- 2. Impor Modul Lokal ---
from app.config import Config
from app.ocr.processor import extract_bukti_setor_data
from app.utils.helpers import allowed_file

# ==============================================================================
# Inisialisasi Aplikasi Flask & Ekstensi
# ==============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Add ProxyFix for deployment behind reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Setup logging
logging.basicConfig(
    level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Batasi ukuran file upload 
app.config['MAX_CONTENT_LENGTH'] = app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)

# Inisialisasi CORS dengan konfigurasi yang lebih fleksibel
cors_origins = app.config.get('CORS_ORIGINS', [
    "http://localhost:3000",
    "https://proyek-pajak.vercel.app"
])
if isinstance(cors_origins, str):
    cors_origins = cors_origins.split(",")

# Add environment variable for frontend URL
if os.environ.get("FRONTEND_URL"):
    cors_origins.append(os.environ.get("FRONTEND_URL"))

CORS(app, origins=cors_origins, supports_credentials=True)

# Membuat folder upload jika belum ada
upload_folder = app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    app.logger.info(f"📁 Created upload folder: {upload_folder}")

# ==============================================================================
# Definisi Endpoint API (Routes)
# ==============================================================================

@app.route("/")
def index():
    """Endpoint dasar untuk memeriksa apakah server berjalan."""
    return "Hello from EasyOCR Stateless API!"

@app.route("/health")
def health_check():
    """Health check endpoint yang komprehensif."""
    try:
        # Basic health metrics
        import psutil
        import gc
        
        # Memory info
        memory_info = psutil.virtual_memory()
        
        health_data = {
            "status": "ok",
            "message": "Service is running",
            "ready": True,
            "timestamp": time.time(),
            "system": {
                "memory_percent": memory_info.percent,
                "memory_available": memory_info.available // (1024*1024),  # MB
                "cpu_percent": psutil.cpu_percent(interval=1),
            },
            "app": {
                "upload_folder": app.config['UPLOAD_FOLDER'],
                "max_file_size": app.config['MAX_CONTENT_LENGTH'] // (1024*1024),  # MB
                "flask_env": app.config.get('FLASK_ENV', 'unknown')
            }
        }
        
        return jsonify(health_data), 200
        
    except ImportError:
        # Fallback if psutil not available
        return jsonify({
            "status": "ok", 
            "message": "Service is running (basic check)",
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
    """Deep health check yang mengecek EasyOCR dan dependencies."""
    try:
        from app.ocr.ocr_engine import get_ocr_reader
        import torch
        import cv2
        
        # Check OCR availability
        ocr_reader = get_ocr_reader()
        ocr_status = ocr_reader is not None
        
        health_data = {
            "status": "ok" if ocr_status else "warning",
            "message": "Service is fully healthy" if ocr_status else "OCR not ready",
            "ready": True,
            "ocr_ready": ocr_status,
            "dependencies": {
                "torch_version": torch.__version__,
                "opencv_version": cv2.__version__,
                "cuda_available": torch.cuda.is_available(),
                "torch_threads": torch.get_num_threads()
            }
        }
        
        return jsonify(health_data), 200 if ocr_status else 503
        
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
    
    print(f"🚀 Starting EasyOCR Application on port {port}")
    print(f"📁 Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    # 'host="0.0.0.0"' membuat server dapat diakses dari luar container Docker
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
