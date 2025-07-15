# bukti_setor/processor.py - Production Optimized OCR Processor
# -*- coding: utf-8 -*-

import os
import gc
import logging
import traceback
import cv2
import numpy as np
import pytesseract
from flask import jsonify
from pdf2image import convert_from_path
from PIL import Image
from bukti_setor.extractors import (
    extract_kode_setor, extract_tanggal_setor, 
    extract_jumlah_setor, extract_ntpn
)
from utils.file_utils import allowed_file, simpan_preview_image

# Setup logging
logger = logging.getLogger(__name__)

# Memory-optimized OCR configuration
TESSERACT_CONFIG = '--oem 3 --psm 6 -l ind+eng'
MAX_IMAGE_SIZE = (1920, 1080)  # Limit image size to save memory

def preprocess_for_ocr(img):
    """Memory-optimized image preprocessing for OCR"""
    try:
        # Resize image if too large to save memory
        height, width = img.shape[:2]
        if width > MAX_IMAGE_SIZE[0] or height > MAX_IMAGE_SIZE[1]:
            scale = min(MAX_IMAGE_SIZE[0]/width, MAX_IMAGE_SIZE[1]/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Adaptive threshold for better text detection
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Light noise reduction
        kernel = np.ones((1,1), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Force garbage collection
        del gray
        gc.collect()
        
        return thresh
        
    except Exception as e:
        logger.error(f"❌ Preprocessing error: {e}")
        # Return original image as fallback
        return img

def process_bukti_setor_file(request, config):
    """Memory-optimized bukti setor processing"""
    if "file" not in request.files:
        return jsonify(error="File tidak ditemukan"), 400

    file = request.files["file"]
    
    if not allowed_file(file.filename):
        return jsonify(error="Format file tidak didukung"), 400

    # Create upload folder if not exists
    upload_folder = config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save temporary file
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    try:
        logger.info(f"📄 Processing file: {file.filename}")
        
        # Convert PDF to images if needed (memory optimized)
        if file.filename.lower().endswith(".pdf"):
            try:
                # Limit PDF pages to save memory
                images = convert_from_path(filepath, first_page=1, last_page=3)
            except Exception as e:
                logger.error(f"PDF conversion error: {e}")
                return jsonify(error="PDF tidak dapat diproses"), 500
        else:
            try:
                with Image.open(filepath) as img:
                    # Copy to prevent file lock
                    images = [img.copy()]
            except Exception as e:
                logger.error(f"Image loading error: {e}")
                return jsonify(error="Gambar tidak dapat dimuat"), 500

        hasil_semua_halaman = []

        for i, image in enumerate(images):
            halaman_ke = i + 1
            logger.info(f"� Processing page {halaman_ke}")

            try:
                # Convert PIL to OpenCV format (memory optimized)
                if isinstance(image, np.ndarray):
                    img_cv = image
                else:
                    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Preprocessing untuk OCR
                thresh = preprocess_for_ocr(img_cv)

                # Simpan preview image
                preview_filename = simpan_preview_image(
                    pil_image=image,
                    upload_folder=upload_folder,
                    page_num=halaman_ke,
                    original_filename=file.filename
                )

                # OCR dengan Tesseract (optimized config)
                raw_text = pytesseract.image_to_string(thresh, config=TESSERACT_CONFIG)
                logger.info(f"✅ OCR completed for page {halaman_ke}")

                # Ekstraksi data dari OCR
                kode_setor = extract_kode_setor(raw_text)
                tanggal_setor = extract_tanggal_setor(raw_text)
                jumlah_setor = extract_jumlah_setor(raw_text)
                ntpn = extract_ntpn(raw_text)

                # Format hasil
                hasil_halaman = {
                    "kode_setor": kode_setor,
                    "tanggal": tanggal_setor.strftime("%Y-%m-%d") if tanggal_setor else "",
                    "jumlah": jumlah_setor,
                    "ntpn": ntpn,
                    "halaman": halaman_ke,
                    "preview_filename": preview_filename,
                    "raw_ocr": raw_text[:200] + "..." if len(raw_text) > 200 else raw_text,  # Limit raw text size
                }

                # Tambahkan warning jika data tidak lengkap
                missing_fields = []
                if not kode_setor:
                    missing_fields.append("Kode Setor")
                if not tanggal_setor:
                    missing_fields.append("Tanggal")
                if not jumlah_setor:
                    missing_fields.append("Jumlah")
                    
                if missing_fields:
                    hasil_halaman["warning_message"] = f"Data tidak terdeteksi: {', '.join(missing_fields)}"

                hasil_semua_halaman.append(hasil_halaman)
                
                # Memory cleanup
                del img_cv, thresh
                if 'raw_text' in locals():
                    del raw_text
                gc.collect()
                
            except Exception as e:
                logger.error(f"❌ Error processing page {halaman_ke}: {e}")
                # Add fallback data for failed page
                hasil_halaman = {
                    "kode_setor": "",
                    "tanggal": "",
                    "jumlah": 0,
                    "ntpn": "",
                    "halaman": halaman_ke,
                    "preview_filename": f"error_page_{halaman_ke}.jpg",
                    "raw_ocr": "",
                    "error_message": f"Gagal memproses halaman {halaman_ke}: {str(e)}"
                }
                hasil_semua_halaman.append(hasil_halaman)

        # Final memory cleanup
        if 'images' in locals():
            del images
        gc.collect()

        return jsonify({
            "success": True,
            "data": hasil_semua_halaman,
            "total_halaman": len(hasil_semua_halaman),
            "message": f"✅ Berhasil memproses {len(hasil_semua_halaman)} halaman"
        }), 200

    except Exception as err:
        logger.error(f"❌ Processing error: {err}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Gagal memproses file",
            "message": str(err),
            "fallback_available": True
        }), 500

    finally:
        # Cleanup temporary file
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Cleaned up temporary file: {file.filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup file: {e}")
        
        # Force memory cleanup
        gc.collect()
