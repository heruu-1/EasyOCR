# bukti_setor/processor.py
# -*- coding: utf-8 -*-
# File untuk memproses bukti setor pajak dengan OCR

import os
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

def preprocess_for_ocr(img):
    """Preprocessing gambar untuk OCR yang lebih baik"""
    # Konversi ke grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Adaptive threshold untuk binarization
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Noise reduction
    kernel = np.ones((1,1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.medianBlur(thresh, 3)
    
    return thresh

def process_bukti_setor_file(request, config):
    """Fungsi utama untuk memproses file bukti setor"""
    if "file" not in request.files:
        return jsonify(error="File tidak ditemukan"), 400

    file = request.files["file"]

    if not allowed_file(file.filename):
        return jsonify(error="File tidak didukung. Gunakan PDF atau gambar"), 400

    # Simpan file sementara
    filepath = os.path.join(config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        # Konversi PDF ke gambar jika perlu
        if file.filename.lower().endswith(".pdf"):
            images = convert_from_path(filepath)
        else:
            with Image.open(filepath) as img:
                images = [img.copy()]

        hasil_semua_halaman = []

        for i, image in enumerate(images):
            halaman_ke = i + 1
            print(f"\n=== [📝 DEBUG] MEMPROSES HALAMAN BUKTI SETOR {halaman_ke} ===")

            # Konversi PIL ke OpenCV format
            if isinstance(image, np.ndarray):
                img_cv = image
            else:
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocessing untuk OCR
            thresh = preprocess_for_ocr(img_cv)

            # Simpan preview image
            preview_filename = simpan_preview_image(
                pil_image=image,
                upload_folder=config['UPLOAD_FOLDER'],
                page_num=halaman_ke,
                original_filename=file.filename
            )

            # OCR dengan Tesseract
            raw_text = pytesseract.image_to_string(img_cv, lang="ind", config="--psm 6")
            print(f"[📄 RAW OCR TEXT] Halaman {halaman_ke}:")
            print(raw_text)
            print("=" * 50)

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
                "raw_ocr": raw_text,
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
                hasil_halaman["warning_message"] = (
                    f"Data tidak terdeteksi: {', '.join(missing_fields)}. "
                    "Mohon isi manual."
                )

            hasil_semua_halaman.append(hasil_halaman)

        return (
            jsonify(
                {
                    "success": True,
                    "data": hasil_semua_halaman,
                    "total_halaman": len(images),
                    "message": f"Berhasil memproses {len(images)} halaman"
                }
            ),
            200,
        )

    except Exception as err:
        print(f"[❌ ERROR] {traceback.format_exc()}")
        return jsonify(error=str(err)), 500

    finally:
        # Bersihkan file sementara
        if os.path.exists(filepath):
            os.remove(filepath)
