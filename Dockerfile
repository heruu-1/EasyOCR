# File: Dockerfile
# Deskripsi: Resep optimasi agresif untuk memaksa ukuran image menjadi kecil.

# Memulai dari base image yang spesifik dan ringan
FROM python:3.10-slim-bullseye

# Menetapkan beberapa variabel lingkungan untuk praktik terbaik
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Menetapkan direktori kerja
WORKDIR /app

# Menginstal dependensi sistem yang dibutuhkan saat runtime,
# lalu langsung membersihkan cache apt untuk menghemat ruang.
RUN apt-get update && \
    apt-get install -y --no-install-recommends poppler-utils libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Membuat virtual environment untuk isolasi dependensi.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Meng-upgrade pip dan menginstal wheel untuk build yang lebih cepat
RUN pip install --no-cache-dir --upgrade pip wheel

# Menyalin file requirements.txt
COPY requirements.txt .

# --- LANGKAH KUNCI PENGINSTALAN ---
# 1. Instal PyTorch versi CPU-only SECARA EKSPLISIT. Ini yang paling penting.
RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu

# 2. Instal easyocr SETELAH torch terinstal.
RUN pip install --no-cache-dir easyocr

# 3. Instal sisa dependensi dari requirements.txt.
#    Pip akan melihat torch sudah ada dan tidak akan menginstalnya lagi.
RUN pip install --no-cache-dir -r requirements.txt

# --- TAHAP PEMBERSIHAN EKSTREM ---
# Membersihkan semua cache yang mungkin tersisa untuk mengecilkan ukuran akhir
RUN rm -rf /root/.cache

# Menyalin kode aplikasi Anda
COPY ./app /app/app

# Menetapkan port
EXPOSE 5000

# Menjalankan aplikasi menggunakan python dari virtual environment
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app.app:app"]