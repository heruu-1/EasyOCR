# File: app/ocr/processor.py
# Deskripsi: Modul orkestrasi utama untuk pipeline pemrosesan OCR.
# File ini mengambil file input, mengoordinasikan pra-pemrosesan,
# menjalankan engine EasyOCR, dan mendelegasikan ekstraksi data ke parser spesialis.

import time
from PIL import Image
import numpy as np
import cv2
from pdf2image import convert_from_path
from flask import current_app

# --- Impor Lokal dari Struktur Proyek ---

# 1. Komponen Inti OCR
from app.ocr.ocr_engine import OCR_READER
from app.ocr.spellcheck import correct_spelling

# 2. Fungsi Utilitas
# Asumsi 'helpers.py' ada di 'app/utils/'
from app.utils.helpers import simpan_preview_image, preprocess_for_ocr

# 3. Parser Ekstraksi Data
from app.extractor.tanggal import parse_tanggal
from app.extractor.jumlah import parse_jumlah
from app.extractor.kode_setor import parse_kode_setor


def _extract_data_from_image(pil_image, upload_folder, page_num=1):
    """
    Memproses satu gambar (halaman) melalui pipeline OCR lengkap.

    Args:
        pil_image (PIL.Image.Image): Objek gambar dari PIL.
        upload_folder (str): Path ke folder untuk menyimpan preview.
        page_num (int): Nomor halaman (untuk penamaan file).

    Returns:
        dict: Dictionary berisi data yang telah diekstrak.
    """
    # Menyimpan gambar preview untuk ditampilkan di UI.
    # Ini adalah langkah pertama agar pengguna bisa melihat apa yang sedang diproses.
    preview_filename = simpan_preview_image(
        pil_image=pil_image,
        upload_folder=upload_folder,
        page_num=page_num
    )

    # --- Tahap Pra-Pemrosesan Gambar (Image Pre-processing) ---

    # 1. Konversi dari format PIL (RGB) ke format OpenCV (BGR)
    img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # 2. Standardisasi Ukuran Gambar
    # Mencegah overhead pada gambar beresolusi sangat tinggi dan menstandardisasi input.
    # Kurangi ukuran maksimal untuk deployment
    MAX_WIDTH = 800  # Dikurangi dari 1200 untuk menghemat memory
    if img_cv.shape[1] > MAX_WIDTH:
        ratio = MAX_WIDTH / img_cv.shape[1]
        img_cv = cv2.resize(img_cv, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)
        
    # Optimization: Batasi tinggi juga
    MAX_HEIGHT = 1000
    if img_cv.shape[0] > MAX_HEIGHT:
        ratio = MAX_HEIGHT / img_cv.shape[0]
        img_cv = cv2.resize(img_cv, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)

    # 3. Terapkan Denoising
    # Memanggil fungsi dari utils untuk membersihkan noise pada gambar.
    processed_img = preprocess_for_ocr(img_cv)

    # --- Tahap OCR dan Koreksi Teks ---

    # 4. Jalankan EasyOCR pada gambar yang sudah bersih
    # `paragraph=False` mengembalikan teks per baris, lebih mudah diproses.
    ocr_results = OCR_READER.readtext(processed_img, detail=1, paragraph=False)

    # 5. Pembersihan dan Koreksi Ejaan
    # a. Ambil teksnya saja, bersihkan spasi, dan ubah ke huruf kecil.
    cleaned_ocr = [res[1].strip().lower() for res in ocr_results if len(res[1].strip()) >= 3]
    # b. Terapkan spellchecker kustom pada setiap blok teks.
    all_text_blocks = [correct_spelling(text) for text in cleaned_ocr]
    # c. Gabungkan semua blok menjadi satu string besar untuk parser yang butuh konteks luas.
    full_text_str = " ".join(all_text_blocks)

    # --- Tahap Ekstraksi Data (Parsing) ---

    # 6. Panggil setiap parser spesialis dengan data yang sudah bersih.
    kode_setor = parse_kode_setor(full_text_str)
    tanggal_obj = parse_tanggal(all_text_blocks)
    jumlah = parse_jumlah(all_text_blocks)

    # 7. Susun hasil ke dalam format dictionary yang rapi.
    return {
        "kode_setor": kode_setor,
        "jumlah": jumlah,
        "tanggal": tanggal_obj.isoformat() if tanggal_obj else None,
        "preview_image": preview_filename  # Mengembalikan nama file preview
    }


def extract_bukti_setor_data(filepath, poppler_path=None):
    """
    Fungsi utama yang dipanggil oleh endpoint API.
    Menangani logika untuk file PDF multi-halaman atau gambar tunggal.

    Args:
        filepath (str): Path lengkap ke file yang diunggah.
        poppler_path (str, optional): Path ke instalasi Poppler. Defaults to None.

    Raises:
        ConnectionError: Jika EasyOCR reader tidak berhasil diinisialisasi.

    Returns:
        list: Sebuah list berisi dictionary hasil ekstraksi untuk setiap halaman.
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']

    # Pengaman: Pastikan EasyOCR sudah siap sebelum melanjutkan.
    if not OCR_READER:
        current_app.logger.error("EasyOCR reader tidak berhasil diinisialisasi.")
        # Coba inisialisasi ulang
        try:
            from app.ocr.ocr_engine import initialize_ocr
            if not initialize_ocr():
                raise ConnectionError("EasyOCR reader tidak berhasil diinisialisasi setelah retry.")
        except Exception as e:
            current_app.logger.error(f"Gagal menginisialisasi EasyOCR: {e}")
            raise ConnectionError("EasyOCR reader tidak berhasil diinisialisasi.")

    list_of_results = []

    # Logika untuk membedakan pemrosesan PDF dan gambar
    if filepath.lower().endswith('.pdf'):
        # Konversi semua halaman PDF menjadi daftar gambar PIL
        all_pages_as_images = convert_from_path(filepath, poppler_path=poppler_path)
        # Proses setiap gambar (halaman) satu per satu
        for i, page_image in enumerate(all_pages_as_images):
            result_data = _extract_data_from_image(page_image, upload_folder, page_num=i + 1)
            list_of_results.append(result_data)
    else:
        # Jika bukan PDF, perlakukan sebagai file gambar tunggal
        pil_image = Image.open(filepath)
        result_data = _extract_data_from_image(pil_image, upload_folder, page_num=1)
        list_of_results.append(result_data)

    return list_of_results