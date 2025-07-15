# utils/file_utils.py

import os
import re
import hashlib
from io import BytesIO
from PIL import Image

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    """Cek apakah file diizinkan berdasarkan ekstensi"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    """Cek apakah file adalah gambar"""
    return filename.lower().endswith((".jpg", ".jpeg", ".png"))

def is_valid_image(path):
    """Validasi apakah file gambar valid"""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False

def simpan_preview_image(pil_image, upload_folder, page_num=1, original_filename="preview"):
    """
    Simpan preview image untuk ditampilkan di frontend
    """
    try:
        # Pastikan folder upload ada
        os.makedirs(upload_folder, exist_ok=True)
        
        # Konversi ke RGB jika perlu
        pil_image = pil_image.convert("RGB")
        
        # Buat buffer untuk menyimpan gambar
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()
        
        # Buat hash untuk nama file unik
        img_hash = hashlib.md5(img_bytes).hexdigest()
        
        # Buat nama file yang aman
        safe_name = os.path.splitext(os.path.basename(original_filename))[0]
        safe_name = re.sub(r'[^\w\-_.]', '_', safe_name)  # Hapus karakter tidak aman
        filename = f"{safe_name}_hal_{page_num}_{img_hash[:8]}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        # Simpan jika belum ada
        if not os.path.exists(filepath):
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            print(f"[📸 PREVIEW DISIMPAN] {filename}")
        else:
            print(f"[📎 PREVIEW SUDAH ADA] {filename}")
        
        return filename
        
    except Exception as e:
        print(f"[❌ ERROR SIMPAN PREVIEW] {e}")
        return None
