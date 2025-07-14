# File: Dockerfile
# Deskripsi: Resep untuk membangun container image aplikasi Flask EasyOCR.

# --- Tahap 1: Base Image ---
# Memulai dari image Python 3.10 versi slim yang ringan.
FROM python:3.10-slim

# Menetapkan direktori kerja di dalam container.
# Semua perintah selanjutnya akan dijalankan dari direktori ini.
WORKDIR /app

# --- Tahap 2: Instalasi Dependensi Sistem ---
# Beberapa pustaka Python (seperti OpenCV dan pdf2image) membutuhkan
# dependensi di level sistem operasi.
# - poppler-utils: Dibutuhkan oleh 'pdf2image' untuk konversi PDF.
# - libgl1-mesa-glx: Dependensi umum untuk 'opencv-python-headless'.
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Tahap 3: Instalasi Dependensi Python ---
# Menyalin file requirements.txt terlebih dahulu.
# Ini memanfaatkan Docker caching: jika file ini tidak berubah,
# lapisan ini tidak akan dibangun ulang, mempercepat proses build.
COPY requirements.txt .

# Menginstal semua pustaka Python dari requirements.txt.
# --no-cache-dir mengurangi ukuran image.
RUN pip install --no-cache-dir -r requirements.txt

# --- Tahap 4: Menyalin Kode Aplikasi ---
# Menyalin seluruh isi direktori 'app' dari host ke dalam container.
COPY ./app /app/app

# --- Tahap 5: Konfigurasi Jaringan & Eksekusi ---
# Memberi tahu Docker bahwa container akan mendengarkan di port 5000.
# Port ini harus sesuai dengan yang digunakan oleh Gunicorn.
EXPOSE 5000

# Perintah untuk menjalankan aplikasi saat container dimulai.
# Menggunakan Gunicorn sebagai server WSGI yang siap produksi.
# --bind 0.0.0.0:5000 membuat aplikasi dapat diakses dari luar container.
# app.app:app berarti: dari file app.py di dalam package app, jalankan objek bernama 'app'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app.app:app"]