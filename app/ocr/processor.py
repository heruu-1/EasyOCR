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
from app.ocr.ocr_engine import get_ocr_reader
from app.ocr.spellcheck import correct_spelling

# 2. Fungsi Utilitas
# Asumsi 'helpers.py' ada di 'app/utils/'
from app.utils.helpers import simpan_preview_image, preprocess_for_ocr

# 3. Parser Ekstraksi Data
from app.extractor.tanggal import parse_tanggal
from app.extractor.jumlah import parse_jumlah
from app.extractor.kode_setor import parse_kode_setor


import time
import gc
import os
from PIL import Image
import numpy as np
import cv2
from pdf2image import convert_from_path
from flask import current_app

# --- Impor Lokal dari Struktur Proyek ---

# 1. Komponen Inti OCR
from app.ocr.ocr_engine import get_ocr_reader
from app.ocr.spellcheck import correct_spelling

# 2. Fungsi Utilitas
from app.utils.helpers import simpan_preview_image, preprocess_for_ocr

# 3. Parser Ekstraksi Data
from app.extractor.tanggal import parse_tanggal
from app.extractor.jumlah import parse_jumlah
from app.extractor.kode_setor import parse_kode_setor


def _extract_data_from_image(pil_image, upload_folder, page_num=1, original_filename="preview"):
    """
    Memproses satu gambar (halaman) melalui pipeline OCR lengkap.

    Args:
        pil_image (PIL.Image.Image): Objek gambar dari PIL.
        upload_folder (str): Path ke folder untuk menyimpan preview.
        page_num (int): Nomor halaman (untuk penamaan file).
        original_filename (str): Nama file asli untuk preview.

    Returns:
        dict: Dictionary berisi data yang telah diekstrak.
    """
    start_time = time.time()
    current_app.logger.info(f"🔄 Processing page {page_num}...")
    
    try:
        # Menyimpan gambar preview untuk ditampilkan di UI.
        preview_filename = simpan_preview_image(
            pil_image=pil_image,
            upload_folder=upload_folder,
            page_num=page_num,
            original_filename=original_filename
        )

        # --- Tahap Pra-Pemrosesan Gambar (Image Pre-processing) ---

        # 1. Konversi dari format PIL (RGB) ke format OpenCV (BGR)
        img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # 2. Standardisasi Ukuran Gambar dengan optimasi memory
        MAX_WIDTH = 800  # Dikurangi untuk menghemat memory
        MAX_HEIGHT = 1000
        original_height, original_width = img_cv.shape[:2]
        
        # Calculate optimal size
        width_ratio = MAX_WIDTH / original_width if original_width > MAX_WIDTH else 1
        height_ratio = MAX_HEIGHT / original_height if original_height > MAX_HEIGHT else 1
        ratio = min(width_ratio, height_ratio)
        
        if ratio < 1:
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)
            current_app.logger.info(f"📐 Resized image from {original_width}x{original_height} to {new_width}x{new_height}")

        # 3. Terapkan Denoising
        processed_img = preprocess_for_ocr(img_cv)
        
        # Free memory
        del img_cv
        gc.collect()

        # --- Tahap OCR dan Koreksi Teks ---

        # 4. Jalankan EasyOCR pada gambar yang sudah bersih
        ocr_reader = get_ocr_reader()
        if not ocr_reader:
            raise ConnectionError("EasyOCR reader tidak berhasil diinisialisasi.")
        
        current_app.logger.info("🔍 Running OCR...")
        ocr_results = ocr_reader.readtext(processed_img, detail=1, paragraph=False)
        
        # Free processed image memory
        del processed_img
        gc.collect()

        # 5. Pembersihan dan Koreksi Ejaan
        cleaned_ocr = []
        for res in ocr_results:
            if len(res) >= 2 and len(res[1].strip()) >= 3:
                cleaned_ocr.append(res[1].strip().lower())
        
        # Apply spell checking in batches to save memory
        all_text_blocks = []
        batch_size = 10
        for i in range(0, len(cleaned_ocr), batch_size):
            batch = cleaned_ocr[i:i+batch_size]
            corrected_batch = [correct_spelling(text) for text in batch]
            all_text_blocks.extend(corrected_batch)
            
        full_text_str = " ".join(all_text_blocks)

        # --- Tahap Ekstraksi Data (Parsing) ---

        current_app.logger.info("📊 Extracting data...")
        kode_setor = parse_kode_setor(full_text_str)
        tanggal_obj = parse_tanggal(all_text_blocks)
        jumlah = parse_jumlah(all_text_blocks)

        # Cleanup
        del all_text_blocks, cleaned_ocr, ocr_results
        gc.collect()

        processing_time = time.time() - start_time
        current_app.logger.info(f"✅ Page {page_num} processed in {processing_time:.2f}s")

        return {
            "kode_setor": kode_setor,
            "jumlah": jumlah,
            "tanggal": tanggal_obj.isoformat() if tanggal_obj else None,
            "preview_image": preview_filename,
            "processing_time": round(processing_time, 2),
            "page_number": page_num
        }
        
    except Exception as e:
        current_app.logger.error(f"❌ Error processing page {page_num}: {str(e)}")
        # Cleanup on error
        gc.collect()
        raise


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
    start_time = time.time()
    upload_folder = current_app.config['UPLOAD_FOLDER']
    original_filename = os.path.basename(filepath)
    
    current_app.logger.info(f"🚀 Starting processing for file: {original_filename}")

    # Pengaman: Pastikan EasyOCR sudah siap sebelum melanjutkan.
    try:
        ocr_reader = get_ocr_reader()
        if not ocr_reader:
            current_app.logger.error("EasyOCR reader tidak berhasil diinisialisasi.")
            # Coba inisialisasi ulang
            from app.ocr.ocr_engine import initialize_ocr
            if not initialize_ocr():
                raise ConnectionError("EasyOCR reader tidak berhasil diinisialisasi setelah retry.")
            ocr_reader = get_ocr_reader()
            if not ocr_reader:
                raise ConnectionError("EasyOCR reader masih tidak tersedia setelah retry.")
    except Exception as e:
        current_app.logger.error(f"Gagal menginisialisasi EasyOCR: {e}")
        raise ConnectionError("EasyOCR reader tidak berhasil diinisialisasi.")

    list_of_results = []

    try:
        # Logika untuk membedakan pemrosesan PDF dan gambar
        if filepath.lower().endswith('.pdf'):
            current_app.logger.info(f"📄 Processing PDF with {poppler_path or 'default'} poppler")
            
            # Konversi PDF dengan optimasi memory
            pdf_pages = convert_from_path(
                filepath, 
                poppler_path=poppler_path,
                dpi=150,  # Reduced DPI for memory optimization
                first_page=1,
                last_page=10  # Limit max pages to prevent memory issues
            )
            
            current_app.logger.info(f"📄 PDF converted to {len(pdf_pages)} pages")
            
            # Proses setiap gambar (halaman) satu per satu dengan cleanup
            for i, page_image in enumerate(pdf_pages):
                try:
                    result_data = _extract_data_from_image(
                        page_image, 
                        upload_folder, 
                        page_num=i + 1,
                        original_filename=original_filename
                    )
                    list_of_results.append(result_data)
                    
                    # Clean up page image immediately
                    del page_image
                    gc.collect()
                    
                except Exception as page_error:
                    current_app.logger.error(f"Error processing page {i+1}: {page_error}")
                    # Continue with next page instead of failing completely
                    list_of_results.append({
                        "error": f"Failed to process page {i+1}: {str(page_error)}",
                        "page_number": i + 1
                    })
            
            # Clean up all pages
            del pdf_pages
            gc.collect()
            
        else:
            current_app.logger.info(f"🖼️ Processing single image file")
            
            # Process single image with memory management
            try:
                pil_image = Image.open(filepath)
                # Convert to RGB if necessary
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                    
                result_data = _extract_data_from_image(
                    pil_image, 
                    upload_folder, 
                    page_num=1,
                    original_filename=original_filename
                )
                list_of_results.append(result_data)
                
                # Clean up
                del pil_image
                gc.collect()
                
            except Exception as img_error:
                current_app.logger.error(f"Error processing image: {img_error}")
                raise

        total_time = time.time() - start_time
        current_app.logger.info(f"🎉 Processing completed in {total_time:.2f}s for {len(list_of_results)} pages")
        
        # Add summary to results
        summary = {
            "total_pages": len(list_of_results),
            "total_processing_time": round(total_time, 2),
            "file_type": "PDF" if filepath.lower().endswith('.pdf') else "IMAGE",
            "filename": original_filename
        }
        
        return {
            "summary": summary,
            "results": list_of_results
        }

    except Exception as e:
        current_app.logger.error(f"Critical error in extract_bukti_setor_data: {e}")
        # Force cleanup on error
        gc.collect()
        raise

    finally:
        # Final cleanup
        gc.collect()