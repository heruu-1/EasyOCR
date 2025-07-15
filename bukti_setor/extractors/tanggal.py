# bukti_setor/extractors/tanggal.py
# Ekstraksi tanggal dari bukti setor pajak

import re
from datetime import datetime

def extract_tanggal_setor(raw_text):
    """
    Ekstraksi tanggal dari teks OCR bukti setor
    """
    try:
        tanggal_obj = None
        
        # Pattern untuk format tanggal Indonesia
        bulan_list = "Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember"
        
        patterns = [
            # Format: DD Bulan YYYY (contoh: 15 Januari 2024)
            rf"(\d{{1,2}})\s+({bulan_list})\s+(\d{{4}})",
            
            # Format: DD/MM/YYYY atau DD-MM-YYYY
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            
            # Format: YYYY/MM/DD atau YYYY-MM-DD
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
            
            # Format dengan kata kunci
            r"tanggal\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            r"tgl\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            r"date\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        ]
        
        # Coba pattern tanggal Indonesia dulu
        match_indonesia = re.search(patterns[0], raw_text, re.IGNORECASE)
        if match_indonesia:
            hari, bulan, tahun = match_indonesia.groups()
            bulan_map = {
                "januari": "January", "februari": "February", "maret": "March",
                "april": "April", "mei": "May", "juni": "June",
                "juli": "July", "agustus": "August", "september": "September",
                "oktober": "October", "november": "November", "desember": "December"
            }
            bulan_inggris = bulan_map.get(bulan.lower())
            if bulan_inggris:
                try:
                    tanggal_obj = datetime.strptime(f"{hari} {bulan_inggris} {tahun}", "%d %B %Y")
                    print(f"[✅ TANGGAL] Format Indonesia: {tanggal_obj.strftime('%Y-%m-%d')}")
                    return tanggal_obj
                except ValueError:
                    pass
        
        # Coba format DD/MM/YYYY
        for pattern in patterns[1:]:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                parts = match.groups()
                try:
                    if len(parts) == 3:
                        # Tentukan format berdasarkan urutan
                        if len(parts[0]) == 4:  # YYYY-MM-DD
                            tanggal_obj = datetime.strptime(f"{parts[0]}-{parts[1]}-{parts[2]}", "%Y-%m-%d")
                        else:  # DD-MM-YYYY
                            tanggal_obj = datetime.strptime(f"{parts[0]}-{parts[1]}-{parts[2]}", "%d-%m-%Y")
                        
                        print(f"[✅ TANGGAL] Format numerik: {tanggal_obj.strftime('%Y-%m-%d')}")
                        return tanggal_obj
                except ValueError:
                    continue
        
        # Cari pola tanggal lain di dekat kata kunci
        lines = raw_text.splitlines()
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['tanggal', 'tgl', 'date', 'setor']):
                # Cari semua angka dalam baris ini
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    try:
                        # Coba beberapa kombinasi
                        for i in range(len(numbers) - 2):
                            day, month, year = numbers[i:i+3]
                            if len(year) == 4 and 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
                                tanggal_obj = datetime(int(year), int(month), int(day))
                                print(f"[✅ TANGGAL] Dari baris: {tanggal_obj.strftime('%Y-%m-%d')}")
                                return tanggal_obj
                    except (ValueError, IndexError):
                        continue
        
        if not tanggal_obj:
            print("[❌ TANGGAL] Tidak ditemukan")
            
        return tanggal_obj
        
    except Exception as e:
        print(f"[ERROR extract_tanggal_setor] {e}")
        return None
