import easyocr
import os
import threading
import time
import gc
import torch

OCR_READER = None
_initialization_lock = threading.Lock()
_initialization_started = False
_last_used = None

def initialize_ocr():
    global OCR_READER, _initialization_started, _last_used
    
    with _initialization_lock:
        if _initialization_started and OCR_READER is not None:
            return True
            
        _initialization_started = True
        
        try:
            print("🔄 Memulai inisialisasi EasyOCR Reader...")
            
            # Set CPU mode untuk konsistensi
            torch.set_num_threads(1)
            
            # Coba GPU dulu jika tersedia, fallback ke CPU
            try:
                if torch.cuda.is_available():
                    OCR_READER = easyocr.Reader(['id', 'en'], gpu=True)
                    print("✅ EasyOCR Reader berhasil diinisialisasi dengan GPU.")
                else:
                    raise Exception("GPU not available")
            except Exception as gpu_error:
                print(f"⚠️ GPU tidak tersedia ({gpu_error}), menggunakan CPU...")
                OCR_READER = easyocr.Reader(['id', 'en'], gpu=False)
                print("✅ EasyOCR Reader berhasil diinisialisasi dengan CPU.")
            
            _last_used = time.time()
            return True
            
        except Exception as e:
            print(f"❌ Error initializing EasyOCR: {e}")
            OCR_READER = None
            return False

def get_ocr_reader():
    """Lazy loading OCR reader with memory management."""
    global OCR_READER, _last_used
    
    # Check if reader exists and is recent (within 1 hour)
    current_time = time.time()
    if OCR_READER is not None and _last_used and (current_time - _last_used) < 3600:
        _last_used = current_time
        return OCR_READER
    
    # Reinitialize if needed
    if OCR_READER is None or (current_time - _last_used) >= 3600:
        print("🔄 Reinitializing OCR reader...")
        cleanup_ocr()
        initialize_ocr()
    
    _last_used = current_time
    return OCR_READER

def cleanup_ocr():
    """Clean up OCR reader to free memory."""
    global OCR_READER
    if OCR_READER is not None:
        print("🧹 Cleaning up OCR reader...")
        del OCR_READER
        OCR_READER = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Jangan inisialisasi saat import - biarkan lazy loading
print("📦 EasyOCR module loaded - will initialize on first use")
