# EasyOCR Bukti Setor

Aplikasi OCR (Optical Character Recognition) khusus untuk memproses bukti setor pajak menggunakan Tesseract OCR dan Flask.

## Fitur

- ✅ **OCR Bukti Setor**: Ekstraksi otomatis data dari gambar/PDF bukti setor pajak
- 📄 **Multi Format**: Support PDF, JPG, JPEG, PNG
- 🔍 **Ekstraksi Data**:
  - Kode Setor (411211, 411121, dll)
  - Tanggal Setor
  - Jumlah Setoran
  - NTPN (Nomor Transaksi Penerimaan Negara)
- 🖼️ **Preview Image**: Tampilan preview hasil OCR
- 🚀 **Ready for Railway**: Siap deploy ke Railway platform

## Instalasi Lokal

### Prerequisites

1. Python 3.11+
2. Tesseract OCR
3. Poppler (untuk PDF)

### Windows

```bash
# Install Tesseract OCR
# Download dari: https://github.com/UB-Mannheim/tesseract/wiki
# Tambahkan ke PATH

# Install Poppler
# Download dari: https://poppler.freedesktop.org/

# Clone repository
git clone <repository-url>
cd EasyOCR

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

### Linux/Ubuntu

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ind poppler-utils

# Clone dan setup
git clone <repository-url>
cd EasyOCR
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

## Docker

```bash
# Build image
docker build -t easyocr-bukti-setor .

# Run container
docker run -p 8000:8000 easyocr-bukti-setor

# Atau menggunakan docker-compose
docker-compose up -d
```

## Deployment ke Railway (Recommended)

### 🚀 Quick Deploy (Simple App)

Untuk deployment cepat dan testing:

1. **Fork/Clone Repository**

   ```bash
   git clone <repository-url>
   cd EasyOCR
   ```

2. **Deploy ke Railway**

   - Buka [Railway.app](https://railway.app)
   - Login dengan GitHub
   - Klik "New Project" → "Deploy from GitHub repo"
   - Pilih repository EasyOCR ini
   - Railway akan auto-detect dan deploy

3. **Test Deployment**
   ```bash
   # Replace 'your-app.railway.app' dengan URL Railway Anda
   python test_app.py your-app.railway.app
   ```

### 📈 Upgrade ke Full OCR

Setelah simple app berhasil, upgrade ke full OCR:

1. **Run Upgrade Script**

   ```bash
   chmod +x upgrade_to_full_ocr.sh
   ./upgrade_to_full_ocr.sh
   ```

2. **Commit dan Push**

   ```bash
   git add .
   git commit -m "Upgrade to full OCR"
   git push
   ```

3. **Monitor Railway Logs**
   - Buka Railway dashboard
   - Lihat deployment logs
   - Test OCR endpoints setelah deployment selesai

## API Endpoints

### 1. Health Check

```
GET /health
```

### 2. Process Bukti Setor

```
POST /api/bukti_setor/process
Content-Type: multipart/form-data

Body:
- file: File bukti setor (PDF/JPG/PNG)
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "kode_setor": "411211",
      "tanggal": "2024-01-15",
      "jumlah": 1500000.0,
      "ntpn": "1234567890123456",
      "halaman": 1,
      "preview_filename": "bukti_hal_1_abc123.jpg",
      "raw_ocr": "..."
    }
  ],
  "total_halaman": 1,
  "message": "Berhasil memproses 1 halaman"
}
```

### 3. Preview Image

```
GET /api/bukti_setor/uploads/<filename>
```

## Struktur Project

```
EasyOCR/
├── app.py                      # Entry point Flask
├── config.py                   # Konfigurasi aplikasi
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── railway.toml               # Railway deployment config
├── docker-compose.yml         # Docker Compose for local dev
├── .env                       # Environment variables
├── bukti_setor/               # Module bukti setor
│   ├── __init__.py
│   ├── processor.py           # Processor utama OCR
│   └── extractors/            # Ekstraksi data spesifik
│       ├── __init__.py
│       ├── kode_setor.py      # Ekstraksi kode setor
│       ├── tanggal.py         # Ekstraksi tanggal
│       ├── jumlah.py          # Ekstraksi jumlah
│       └── ntpn.py            # Ekstraksi NTPN
└── utils/                     # Utilities
    ├── __init__.py
    ├── helpers.py             # Helper functions
    └── file_utils.py          # File utilities
```

## Integrasi dengan Frontend

Aplikasi ini dirancang untuk berintegrasi dengan frontend proyek pajak. Contoh penggunaan:

```javascript
// Frontend integration example
const formData = new FormData();
formData.append("file", buktiSetorFile);

const response = await fetch(
  "https://your-railway-app.railway.app/api/bukti_setor/process",
  {
    method: "POST",
    body: formData,
  }
);

const result = await response.json();
console.log(result.data); // Data hasil OCR
```

## Troubleshooting

### Error: Tesseract not found

- Pastikan Tesseract OCR terinstall dan ada di PATH
- Untuk Railway: sudah include di Dockerfile

### Error: Poppler not found

- Install poppler-utils untuk konversi PDF
- Untuk Railway: sudah include di Dockerfile

### Error: Memory limit

- Optimalkan ukuran gambar sebelum upload
- Gunakan format JPEG dengan kualitas sedang

## License

MIT License

## Support

Untuk bug report atau feature request, silakan buat issue di repository ini.
