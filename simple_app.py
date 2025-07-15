# simple_app.py - Versi sederhana untuk testing deployment
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "message": "EasyOCR Bukti Setor API",
        "version": "1.0.0",
        "status": "active"
    })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "EasyOCR Bukti Setor",
        "port": os.environ.get("PORT", "8000")
    })

@app.route("/api/bukti_setor/process", methods=["POST"])
def process_bukti_setor():
    return jsonify({
        "message": "OCR processing endpoint", 
        "status": "ready",
        "note": "Upload feature will be available after full deployment"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Simple app running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
