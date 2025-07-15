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

## Deployment ke Railway

### Langkah 1: Persiapan

1. Fork/clone repository ini
2. Pastikan semua file ada:
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `nixpacks.toml`
   - `Procfile`

### Langkah 2: Deploy ke Railway

1. Buka [Railway.app](https://railway.app)
2. Login dengan GitHub
3. Klik "New Project" → "Deploy from GitHub repo"
4. Pilih repository EasyOCR ini
5. Railway akan otomatis detect Dockerfile dan deploy

### Langkah 3: Konfigurasi Environment

Tambahkan environment variables di Railway dashboard:

```
PORT=8000
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png
FRONTEND_URL=https://proyek-pajak.vercel.app
SECRET_KEY=your-secret-key-here
```

### Langkah 4: Testing

Setelah deployment selesai, test endpoint:

```bash
# Health check
curl https://your-railway-app.railway.app/health

# Upload bukti setor (contoh)
curl -X POST https://your-railway-app.railway.app/api/bukti_setor/process \
  -F "file=@bukti_setor.jpg"
```

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
