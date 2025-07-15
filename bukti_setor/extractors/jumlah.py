# bukti_setor/extractors/jumlah.py
# Ekstraksi jumlah setoran dari bukti setor pajak

import re

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

def extract_jumlah_setor(raw_text):
    """
    Ekstraksi jumlah setoran dari teks OCR bukti setor
    """
    try:
        jumlah = 0.0
        
        # Pattern untuk mencari jumlah setoran
        patterns = [
            # Dengan label jelas
            r"jumlah\s*setor(?:an)?\s*:?\s*Rp\.?\s*([\d.,]+)",
            r"total\s*setor(?:an)?\s*:?\s*Rp\.?\s*([\d.,]+)",
            r"nominal\s*:?\s*Rp\.?\s*([\d.,]+)",
            r"nilai\s*:?\s*Rp\.?\s*([\d.,]+)",
            r"amount\s*:?\s*Rp\.?\s*([\d.,]+)",
            
            # Tanpa Rp
            r"jumlah\s*setor(?:an)?\s*:?\s*([\d.,]+)",
            r"total\s*setor(?:an)?\s*:?\s*([\d.,]+)",
            r"nominal\s*:?\s*([\d.,]+)",
            r"nilai\s*:?\s*([\d.,]+)",
            
            # Pattern untuk bank/transfer
            r"transfer\s*.*?Rp\.?\s*([\d.,]+)",
            r"debet\s*.*?Rp\.?\s*([\d.,]+)",
            r"debit\s*.*?Rp\.?\s*([\d.,]+)",
            
            # Pattern umum untuk angka besar dengan Rp
            r"Rp\.?\s*([\d.,]{7,})",
        ]
        
        # Cari dengan pattern yang spesifik dulu
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                jumlah_str = match.group(1)
                jumlah = clean_number(jumlah_str)
                if jumlah > 0:
                    print(f"[✅ JUMLAH] Ditemukan: {format_currency(jumlah)} dengan pattern: {pattern}")
                    return jumlah
        
        # Jika tidak ditemukan, cari angka besar (kemungkinan jumlah setoran)
        if jumlah == 0:
            # Cari semua angka yang formatnya seperti uang (minimal 6 digit)
            all_numbers = re.findall(r'[\d.,]{6,}', raw_text)
            
            candidates = []
            for num_str in all_numbers:
                try:
                    num_val = clean_number(num_str)
                    if num_val > 10000:  # Minimal 10 ribu
                        candidates.append(num_val)
                except:
                    continue
            
            if candidates:
                # Pilih kandidat yang paling besar (biasanya jumlah setoran)
                jumlah = max(candidates)
                print(f"[⚠️ JUMLAH] Fallback: {format_currency(jumlah)}")
        
        # Analisis per baris untuk konteks yang lebih baik
        if jumlah == 0:
            lines = raw_text.splitlines()
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in 
                      ['jumlah', 'total', 'nominal', 'setor', 'bayar', 'transfer', 'debet', 'debit']):
                    
                    # Cari angka dalam baris ini
                    numbers = re.findall(r'[\d.,]+', line)
                    for num_str in numbers:
                        try:
                            num_val = clean_number(num_str)
                            if num_val > 10000:  # Minimal 10 ribu
                                jumlah = num_val
                                print(f"[✅ JUMLAH] Dari baris konteks: {format_currency(jumlah)}")
                                return jumlah
                        except:
                            continue
        
        if jumlah == 0:
            print("[❌ JUMLAH] Tidak ditemukan")
            return 0.0
            
        return jumlah
        
    except Exception as e:
        print(f"[ERROR extract_jumlah_setor] {e}")
        return 0.0
