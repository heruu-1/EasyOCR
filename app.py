# ==============================================================================  
# File: app.py - Production OCR Backend for Bukti Setor
# Optimized for Railway 4GB memory limit
# ==============================================================================

import os
import sys
import logging
import gc
from flask import Flask, request, jsonify, send_file

# Setup logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory optimization - disable OpenCV GUI features
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask_cors import CORS
    logger.info("✅ Flask-CORS loaded successfully")
except ImportError:
    logger.warning("⚠️ CORS not available, skipping...")
    CORS = None

try:
    from config import Config
    logger.info("✅ Config loaded successfully")
except ImportError:
    logger.warning("⚠️ Using default configuration...")
    class Config:
        UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
        ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
        SECRET_KEY = os.getenv("SECRET_KEY", "production-secret")

# Import OCR processor with fallback
try:
    from bukti_setor.processor import process_bukti_setor_file
    logger.info("✅ OCR processor loaded successfully")
except ImportError as e:
    logger.error(f"❌ OCR processor import error: {e}")
    def process_bukti_setor_file(request, config):
        return jsonify({
            "error": "OCR processor not available", 
            "message": "Check system dependencies"
        }), 500

app = Flask(__name__)
app.config.from_object(Config)

# CORS setup for production
if CORS:
    CORS(app, origins=[
        "https://proyek-pajak.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000"  # for development only
    ], supports_credentials=True, 
    methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'])
    logger.info("✅ CORS configured for production")
else:
    logger.warning("⚠️ Running without CORS support")

# Memory cleanup after each request
@app.after_request 
def cleanup_memory(response):
    gc.collect()  # Force garbage collection
    return response

# Ensure upload folder exists
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

# ==============================================================================  
# ROUTES  
# ==============================================================================

@app.route("/")
def index():
    return jsonify({
        "message": "EasyOCR Bukti Setor Production API",
        "version": "2.0.0",
        "status": "active",
        "memory_optimized": True
    })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "EasyOCR Bukti Setor Production",
        "cors_enabled": CORS is not None,
        "endpoints": ["/api/bukti_setor/process"]
    })

@app.route("/api/bukti_setor/process", methods=["POST", "OPTIONS"])
def process_bukti_setor():
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"})
        
    logger.info("🚀 Processing bukti setor OCR request")
    try:
        result = process_bukti_setor_file(request, app.config)
        logger.info("✅ OCR processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ OCR processing error: {e}")
        return jsonify({
            "error": "Processing failed", 
            "message": str(e),
            "demo_fallback": {
                "kode_setor": "411211",
                "tanggal": "2024-01-15",
                "jumlah": 1500000,
                "warning": "Using fallback data due to processing error"
            }
        }), 500

@app.route("/api/bukti_setor/uploads/<filename>")
def serve_preview(filename):
    try:
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype="image/jpeg")
        else:
            return jsonify({"error": "Preview not available"}), 404
    except Exception as e:
        logger.error(f"Error serving preview: {e}")
        return jsonify({"error": "Server error"}), 500

# ==============================================================================  
# Entry Point for Production
# ==============================================================================

if __name__ == "__main__":
    # Production configuration
    port = int(os.environ.get("PORT", 8000))
    
    logger.info("� Starting EasyOCR Production Server")
    logger.info(f"   Port: {port}")
    logger.info(f"   Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    logger.info(f"   Memory optimization: enabled")
    
    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    try:
        # Production mode - no debug
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)
