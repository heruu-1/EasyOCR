# ==============================================================================  
# File: app.py  
# Deskripsi: Entry point utama Flask untuk OCR Bukti Setor Pajak
# ==============================================================================

import os
import sys
import traceback
from flask import Flask, request, jsonify, send_file

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask_cors import CORS
except ImportError:
    print("⚠️ CORS not available, skipping...")
    CORS = None

try:
    from config import Config
except ImportError:
    print("⚠️ Using default configuration...")
    class Config:
        UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
        ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
        SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

# Import with fallback
try:
    from bukti_setor.processor import process_bukti_setor_file
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    # Create a simple fallback processor
    def process_bukti_setor_file(request, config):
        return jsonify({
            "error": "OCR processor not available", 
            "message": "Basic API mode"
        }), 500

app = Flask(__name__)
app.config.from_object(Config)

# CORS setup with error handling
if CORS:
    CORS(app, origins=[
        "http://localhost:3000",
        "https://proyek-pajak.vercel.app",
        os.environ.get("FRONTEND_URL")
    ], supports_credentials=True)
else:
    print("⚠️ Running without CORS support")

# Ensure upload folder exists
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

# ==============================================================================  
# ROUTES  
# ==============================================================================

@app.route("/")
def index():
    return jsonify({
        "message": "EasyOCR Bukti Setor API",
        "version": "1.0.0",
        "status": "active"
    })

@app.route("/api/bukti_setor/process", methods=["POST"])
def process_bukti_setor():
    print("🚀 Route /api/bukti_setor/process terpanggil")
    try:
        return process_bukti_setor_file(request, app.config)
    except Exception as e:
        print(f"❌ Error processing: {e}")
        return jsonify({"error": str(e), "message": "Processing failed"}), 500

@app.route("/api/bukti_setor/uploads/<filename>")
def serve_preview(filename):
    try:
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype="image/jpeg")
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "EasyOCR Bukti Setor"})

# ==============================================================================  
# Entry Point  
# ==============================================================================

if __name__ == "__main__":
    # Print configuration info
    print("📦 UPLOAD_FOLDER =", app.config.get('UPLOAD_FOLDER', 'uploads'))
    print("🌐 FRONTEND_URL =", os.getenv("FRONTEND_URL", 'Not set'))
    print("🔧 Environment =", os.getenv("RAILWAY_ENVIRONMENT", "local"))
    
    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.getenv("FLASK_ENV") != "production"
    
    print(f"🚀 Running Flask on http://0.0.0.0:{port}")
    print(f"🔍 Debug mode: {debug_mode}")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=debug_mode)
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)
