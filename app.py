# ==============================================================================  
# File: app.py  
# Deskripsi: Entry point utama Flask untuk OCR Bukti Setor Pajak
# ==============================================================================

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from bukti_setor.processor import process_bukti_setor_file

# ==============================================================================  
# Inisialisasi Flask App  
# ==============================================================================

print("📦 DATABASE_URL =", os.getenv("DATABASE_URL"))
print("🌐 FRONTEND_URL =", os.getenv("FRONTEND_URL"))
print("📁 UPLOAD_FOLDER =", os.getenv("UPLOAD_FOLDER"))

app = Flask(__name__)
app.config.from_object(Config)

# CORS
CORS(app, origins=[
    "http://localhost:3000",
    "https://proyek-pajak.vercel.app",
    os.environ.get("FRONTEND_URL")
], supports_credentials=True)

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
    return process_bukti_setor_file(request, app.config)

@app.route("/api/bukti_setor/uploads/<filename>")
def serve_preview(filename):
    upload_folder = app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    return send_file(filepath, mimetype="image/jpeg")

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "EasyOCR Bukti Setor"})

# ==============================================================================  
# Entry Point  
# ==============================================================================

if __name__ == "__main__":
    # Pastikan folder upload ada
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Running Flask on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
