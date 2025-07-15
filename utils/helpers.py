# utils/helpers.py

import re
from PIL import Image

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def clean_number(text):
    """Convert string seperti 'Rp 1.000.000,00' ke float 1000000.0"""
    if not text:
        return 0.0
    
    # Hapus semua karakter kecuali angka, koma, dan titik
    cleaned_text = re.sub(r"[^\d,.-]", "", text).strip()
    
    try:
        # Handle format Indonesia: 1.000.000,00
        if "," in cleaned_text and "." in cleaned_text:
            # Jika ada keduanya, anggap titik sebagai pemisah ribuan dan koma sebagai desimal
            cleaned_text = cleaned_text.replace(".", "").replace(",", ".")
        elif "." in cleaned_text and "," not in cleaned_text:
            # Jika hanya ada titik, bisa jadi pemisah ribuan atau desimal
            # Jika lebih dari 3 digit setelah titik terakhir, anggap pemisah ribuan
            parts = cleaned_text.split(".")
            if len(parts[-1]) > 2:
                cleaned_text = cleaned_text.replace(".", "")
        elif "," in cleaned_text and "." not in cleaned_text:
            # Jika hanya ada koma, ganti dengan titik untuk desimal
            cleaned_text = cleaned_text.replace(",", ".")
            
        return float(cleaned_text)
    except ValueError:
        return 0.0

def format_currency(value, with_symbol=True):
    """Format angka menjadi format mata uang Indonesia"""
    try:
        value = float(value)
        formatted = f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"Rp {formatted}" if with_symbol else formatted
    except:
        return "Rp 0" if with_symbol else "0"

def clean_string(text):
    """Bersihkan string dari karakter tidak perlu"""
    if not text:
        return ""
    
    # Hapus karakter khusus dan extra whitespace
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().upper()
