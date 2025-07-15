# simple_app.py - Versi sederhana untuk testing deployment
import os
import logging
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

# Setup logging untuk production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress OpenCV/libGL warnings in headless environment
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

app = Flask(__name__)

# CORS Configuration untuk frontend
CORS(app, origins=[
    "http://localhost:3000",
    "https://proyek-pajak.vercel.app",
    "https://*.vercel.app",
    "*"  # Untuk testing, nanti bisa dibatasi
], supports_credentials=True, 
methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])

# Add before_request handler untuk logging
@app.before_request
def log_request_info():
    logger.info(f"🔍 {request.method} {request.url}")
    logger.info(f"   Origin: {request.headers.get('Origin', 'Not set')}")
    logger.info(f"   User-Agent: {request.headers.get('User-Agent', 'Not set')}")
    if request.method == 'POST' and request.is_json:
        logger.info(f"   JSON Data: {request.get_json()}")

# Add after_request handler untuk CORS debugging
@app.after_request
def after_request(response):
    logger.info(f"📤 Response Status: {response.status_code}")
    logger.info(f"   CORS Headers: {dict(response.headers)}")
    return response

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
        "port": os.environ.get("PORT", "8000"),
        "cors_enabled": True,
        "endpoints": [
            "/api/bukti_setor/process",
            "/api/bukti_setor/save", 
            "/api/bukti_setor/history"
        ]
    })

@app.route("/test-cors", methods=["GET", "POST", "OPTIONS"])
def test_cors():
    return jsonify({
        "message": "CORS test successful",
        "method": request.method,
        "origin": request.headers.get('Origin', 'Not set'),
        "headers": dict(request.headers)
    })

@app.route("/api/bukti_setor/process", methods=["POST", "OPTIONS"])
def process_bukti_setor():
    if request.method == "OPTIONS":
        logger.info("🔧 CORS preflight request received")
        response = jsonify({"status": "preflight ok"})
        return response
        
    logger.info("🚀 POST /api/bukti_setor/process endpoint called")
    logger.info(f"   Origin: {request.headers.get('Origin', 'Not set')}")
    logger.info(f"   User-Agent: {request.headers.get('User-Agent', 'Not set')[:50]}...")
    logger.info(f"   Content-Type: {request.headers.get('Content-Type', 'Not set')}")
    logger.info(f"   Files in request: {list(request.files.keys())}")
    logger.info(f"   Form data: {list(request.form.keys())}")
    
    # Simulasi check file upload
    if 'file' not in request.files:
        logger.warning("❌ No file in request")
        return jsonify({
            "error": "No file uploaded",
            "demo_mode": True
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("❌ Empty filename")
        return jsonify({
            "error": "No file selected", 
            "demo_mode": True
        }), 400
    
    logger.info(f"✅ File received: {file.filename} ({file.content_type})")
    
    # Generate demo response
    demo_response = {
        "success": True,
        "data": [{
            "kode_setor": "411211",
            "tanggal": "2024-01-15",
            "jumlah": 1500000,
            "ntpn": "1234567890123456",
            "preview_filename": f"demo_{file.filename}",
            "warning_message": "✨ Demo data - OCR akan aktif setelah full deployment"
        }],
        "message": f"📄 Demo response for file: {file.filename}"
    }
    
    logger.info(f"📤 Sending demo response for: {file.filename}")
    return jsonify(demo_response)

@app.route("/api/bukti_setor/uploads/<filename>")
def serve_preview(filename):
    return jsonify({
        "error": "Preview tidak tersedia pada demo mode"
    }), 404

@app.route("/api/bukti_setor/save", methods=["POST", "OPTIONS"])
def save_bukti_setor():
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"})
        
    try:
        data = request.get_json()
        logger.info(f"💾 Save request data: {data}")
        
        # Validasi basic data
        required_fields = ['kode_setor', 'tanggal', 'jumlah']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing fields: {missing_fields}",
                "demo_mode": True
            }), 400
        
        return jsonify({
            "message": "Demo mode - data would be saved in production",
            "received_data": data,
            "demo_mode": True,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"❌ Error in save endpoint: {e}")
        return jsonify({
            "error": str(e),
            "demo_mode": True
        }), 500

@app.route("/api/bukti_setor/history", methods=["GET", "OPTIONS"])
def get_history():
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"})
        
    return jsonify({
        "message": "Demo mode - no history available yet",
        "data": {
            "data": []  # Frontend expects data.data format
        },
        "demo_mode": True
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Simple app starting on port {port}")
    logger.info(f"   Debug mode: {os.environ.get('FLASK_DEBUG', 'False')}")
    logger.info(f"   Environment: {os.environ.get('FLASK_ENV', 'production')}")
    app.run(host="0.0.0.0", port=port, debug=False)
