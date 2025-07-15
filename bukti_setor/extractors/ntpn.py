# bukti_setor/extractors/ntpn.py
# Ekstraksi NTPN (Nomor Transaksi Penerimaan Negara) dari bukti setor pajak

import re

def extract_ntpn(raw_text):
    """
    Ekstraksi NTPN dari teks OCR bukti setor
    NTPN biasanya berupa 16 digit angka
    """
    try:
        ntpn = ""
        
        # Pattern untuk NTPN
        patterns = [
            # Dengan label jelas
            r"ntpn\s*:?\s*(\d{16})",
            r"nomor\s*transaksi\s*:?\s*(\d{16})",
            r"no\s*transaksi\s*:?\s*(\d{16})",
            r"reference\s*:?\s*(\d{16})",
            r"ref\s*:?\s*(\d{16})",
            
            # Pattern dengan pemisah
            r"ntpn\s*:?\s*(\d{4})\s*(\d{4})\s*(\d{4})\s*(\d{4})",
            r"ntpn\s*:?\s*(\d{4})[-.](\d{4})[-.](\d{4})[-.](\d{4})",
            
            # Pattern umum 16 digit
            r"\b(\d{16})\b",
            
            # Pattern dengan kata kunci di sekitarnya
            r"transaksi\s*.*?(\d{16})",
            r"penerimaan\s*.*?(\d{16})",
            r"billing\s*.*?(\d{16})",
        ]
        
        # Cari dengan pattern yang spesifik dulu
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                if len(match.groups()) == 1:
                    ntpn = match.group(1)
                else:
                    # Gabungkan jika ada pemisah
                    ntpn = ''.join(match.groups())
                
                if len(ntpn) == 16:
                    print(f"[✅ NTPN] Ditemukan: {ntpn} dengan pattern: {pattern}")
                    return ntpn
        
        # Cari di sekitar kata kunci jika tidak ditemukan
        if not ntpn:
            lines = raw_text.splitlines()
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in 
                      ['ntpn', 'transaksi', 'reference', 'billing', 'nomor']):
                    
                    # Cari semua angka 16 digit dalam baris ini
                    numbers = re.findall(r'\b(\d{16})\b', line)
                    if numbers:
                        ntpn = numbers[0]
                        print(f"[✅ NTPN] Dari baris konteks: {ntpn}")
                        return ntpn
                    
                    # Cari angka dengan pemisah
                    separated = re.findall(r'(\d{4})[-.\s](\d{4})[-.\s](\d{4})[-.\s](\d{4})', line)
                    if separated:
                        ntpn = ''.join(separated[0])
                        print(f"[✅ NTPN] Dengan pemisah: {ntpn}")
                        return ntpn
        
        # Fallback: cari semua 16 digit di seluruh teks
        if not ntpn:
            all_16_digits = re.findall(r'\b(\d{16})\b', raw_text)
            if all_16_digits:
                ntpn = all_16_digits[0]  # Ambil yang pertama
                print(f"[⚠️ NTPN] Fallback: {ntpn}")
                return ntpn
        
        if not ntpn:
            print("[❌ NTPN] Tidak ditemukan")
            return "Tidak ditemukan"
            
        return ntpn.strip()
        
    except Exception as e:
        print(f"[ERROR extract_ntpn] {e}")
        return "Tidak ditemukan"
