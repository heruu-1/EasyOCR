import easyocr
import os

OCR_READER = None

def initialize_ocr():
    global OCR_READER
    try:
        print("Inisialisasi EasyOCR Reader...")
        # Coba GPU dulu jika tersedia, fallback ke CPU
        try:
            OCR_READER = easyocr.Reader(['id', 'en'], gpu=True)
            print("✅ EasyOCR Reader berhasil diinisialisasi dengan GPU.")
        except:
            print("⚠️ GPU tidak tersedia, menggunakan CPU...")
            OCR_READER = easyocr.Reader(['id', 'en'], gpu=False)
            print("✅ EasyOCR Reader berhasil diinisialisasi dengan CPU.")
        return True
    except Exception as e:
        print(f"❌ Error initializing EasyOCR: {e}")
        OCR_READER = None
        return False

# Inisialisasi saat import
initialize_ocr()
