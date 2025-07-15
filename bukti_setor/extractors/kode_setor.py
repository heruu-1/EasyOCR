# bukti_setor/extractors/kode_setor.py
# Ekstraksi kode setor dari bukti setor pajak

import re

def extract_kode_setor(raw_text):
    """
    Ekstraksi kode setor dari teks OCR bukti setor
    Kode setor biasanya berupa angka 6-8 digit yang mengidentifikasi jenis pajak
    """
    try:
        kode_setor = ""
        
        # Pattern untuk kode setor yang umum
        # Contoh: 411121, 411211, 411126, dsb
        patterns = [
            # Pola dengan label "kode setor" atau "kode"
            r"kode\s*setor\s*:?\s*(\d{6,8})",
            r"kode\s*:?\s*(\d{6,8})",
            
            # Pola untuk SSP (Surat Setoran Pajak)
            r"ssp\s*.*?(\d{6,8})",
            
            # Pola untuk jenis setoran PPN (411211)
            r"(411211)",
            r"(411121)", # PPN Dalam Negeri
            r"(411126)", # PPN Impor
            r"(411128)", # PPN Final
            
            # Pola untuk PPh 
            r"(411124)", # PPh Pasal 22
            r"(411125)", # PPh Pasal 23
            
            # Pola umum 6-8 digit yang didahului/diikuti kata kunci
            r"setoran\s*.*?(\d{6,8})",
            r"pajak\s*.*?(\d{6,8})",
            r"billing\s*.*?(\d{6,8})",
        ]
        
        # Cari dengan pattern yang spesifik dulu
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                kode_setor = match.group(1)
                print(f"[✅ KODE SETOR] Ditemukan: {kode_setor} dengan pattern: {pattern}")
                break
        
        # Jika tidak ditemukan dengan pattern khusus, cari di seluruh teks
        if not kode_setor:
            # Cari semua angka 6-8 digit
            all_codes = re.findall(r'\b(\d{6,8})\b', raw_text)
            
            # Filter kode yang paling mungkin (dimulai dengan 4)
            likely_codes = [code for code in all_codes if code.startswith('4')]
            
            if likely_codes:
                kode_setor = likely_codes[0]  # Ambil yang pertama
                print(f"[⚠️ KODE SETOR] Fallback: {kode_setor}")
            elif all_codes:
                kode_setor = all_codes[0]  # Fallback ke angka pertama
                print(f"[⚠️ KODE SETOR] Fallback umum: {kode_setor}")
        
        if not kode_setor:
            print("[❌ KODE SETOR] Tidak ditemukan")
            return "Tidak ditemukan"
            
        return kode_setor.strip()
        
    except Exception as e:
        print(f"[ERROR extract_kode_setor] {e}")
        return "Tidak ditemukan"
