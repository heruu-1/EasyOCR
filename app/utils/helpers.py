# bukti_setor/utils/helpers.py

import os
import hashlib
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from flask import current_app

def simpan_preview_image(pil_image, upload_folder, page_num, original_filename="preview"):
    """Menyimpan gambar preview dengan nama yang unik."""
    try:
        pil_image = pil_image.convert("RGB")
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        safe_name = os.path.splitext(os.path.basename(original_filename))[0]
        filename = f"{safe_name}_hal_{page_num}_{img_hash[:8]}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        if not os.path.exists(filepath):
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            current_app.logger.info(f"[📸 PREVIEW DISIMPAN] {filename}")
        else:
            current_app.logger.info(f"[📎 PREVIEW SUDAH ADA] {filename}")
        return filename
    except Exception as e:
        current_app.logger.error(f"[❌ ERROR SIMPAN PREVIEW] {e}")
        return None

def preprocess_for_ocr(image):
    """Memproses gambar untuk OCR dengan denoising."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    return denoised

def allowed_file(filename, allowed_extensions):
    """Memeriksa apakah file memiliki ekstensi yang diizinkan."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def fuzzy_month_match(ocr_month, all_months):
    """Mencari kecocokan bulan dengan fuzzy matching."""
    from thefuzz import fuzz
    
    best_match = None
    best_score = 0
    
    for month_name in all_months.keys():
        score = fuzz.ratio(ocr_month.lower(), month_name.lower())
        if score > best_score and score >= 70:  # Threshold 70%
            best_score = score
            best_match = month_name
    
    return best_match

def clean_transaction_value(value_str):
    """Membersihkan dan mengkonversi string nilai transaksi menjadi integer."""
    if not value_str:
        return None
    
    # Hapus semua karakter non-digit kecuali koma dan titik
    cleaned = ''.join(c for c in value_str if c.isdigit() or c in '.,')
    
    # Hapus leading zeros
    cleaned = cleaned.lstrip('0') or '0'
    
    # Handle different decimal formats
    if ',' in cleaned and '.' in cleaned:
        # Format: 1.234,56 (European) -> 123456
        if cleaned.rindex(',') > cleaned.rindex('.'):
            cleaned = cleaned.replace('.', '').replace(',', '')
        else:
            # Format: 1,234.56 (US) -> 123456
            cleaned = cleaned.replace(',', '').replace('.', '')
    elif ',' in cleaned:
        # Asumsi koma sebagai separator ribuan: 1,234 -> 1234
        cleaned = cleaned.replace(',', '')
    elif '.' in cleaned:
        # Asumsi titik sebagai separator ribuan: 1.234 -> 1234
        cleaned = cleaned.replace('.', '')
    
    try:
        return int(cleaned) if cleaned else None
    except ValueError:
        return None