# File: Dockerfile
# Deskripsi: Versi optimasi menggunakan multi-stage build untuk menghasilkan image yang kecil.

# --- TAHAP 1: BUILDER ---
# Tahap ini fokus untuk menginstal semua dependensi dengan benar.
FROM python:3.10-slim as builder

# Menetapkan direktori kerja
WORKDIR /app

# Menginstal dependensi sistem yang dibutuhkan untuk build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Menyalin file requirements.txt
COPY requirements.txt .

# Menginstal dependensi dengan --prefix untuk isolasi
# Ini akan menginstal semua paket ke dalam folder /app/install
RUN pip install --prefix=/app/install -r requirements.txt

# Menginstal PyTorch versi CPU-only yang jauh lebih kecil
RUN pip install --prefix=/app/install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Menginstal easyocr secara terpisah setelah PyTorch terinstal
RUN pip install --prefix=/app/install easyocr


# --- TAHAP 2: FINAL ---
# Tahap ini fokus untuk membuat image akhir yang ramping.
FROM python:3.10-slim

# Menetapkan direktori kerja
WORKDIR /app

# Menginstal HANYA dependensi sistem yang dibutuhkan saat runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Menyalin pustaka Python yang sudah terinstal dari tahap builder
COPY --from=builder /app/install /usr/local

# Menyalin kode aplikasi Anda
COPY ./app /app/app

# Mengekspos port aplikasi
EXPOSE 5000

# Perintah untuk menjalankan aplikasi
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app.app:app"]