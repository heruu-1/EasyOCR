import easyocr
import os
import threading
import time

OCR_READER = None
_initialization_lock = threading.Lock()
_initialization_started = False

def initialize_ocr():
    global OCR_READER, _initialization_started
    
    with _initialization_lock:
        if _initialization_started:
            return OCR_READER is not None
            
        _initialization_started = True
        
        try:
            print("🔄 Memulai inisialisasi EasyOCR Reader...")
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

def get_ocr_reader():
    """Lazy loading OCR reader."""
    global OCR_READER
    if OCR_READER is None:
        initialize_ocr()
    return OCR_READER

# Jangan inisialisasi saat import - biarkan lazy loading
print("📦 EasyOCR module loaded - will initialize on first use")
