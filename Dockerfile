# =====================================================
# OPTIMIZED PRODUCTION DOCKERFILE FOR EASYOCR
# Fitur: Multi-stage, Non-root user, Healthcheck, Optimisasi Ukuran & Kecepatan
# =====================================================

# =================== STAGE 1: BUILDER ===================
# Tahap ini fokus untuk menginstal semua dependensi dengan benar dan efisien.
FROM python:3.10-slim-bullseye AS builder

# Argumen build untuk fleksibilitas versi di masa depan
ARG TORCH_VERSION=2.1.2
ARG TORCHVISION_VERSION=0.16.2
ARG EASYOCR_VERSION=1.7.0

# Variabel lingkungan untuk optimisasi build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Direktori kerja untuk tahap build
WORKDIR /build

# Menginstal dependensi sistem yang hanya dibutuhkan untuk kompilasi
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Membuat virtual environment untuk isolasi yang bersih
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Meng-upgrade pip dan build tools
RUN pip install --upgrade pip wheel setuptools

# Menyalin requirements.txt untuk memanfaatkan Docker cache
COPY requirements.txt .

# --- URUTAN INSTALASI KRUSIAL ---
# 1. Instal PyTorch versi CPU-only terlebih dahulu untuk menghindari versi GPU yang besar.
RUN pip install \
    torch==${TORCH_VERSION} \
    torchvision==${TORCHVISION_VERSION} \
    --index-url https://download.pytorch.org/whl/cpu

# 2. Instal EasyOCR setelah PyTorch terpasang.
RUN pip install easyocr==${EASYOCR_VERSION}

# 3. Instal sisa dependensi dari requirements.txt.
RUN pip install -r requirements.txt

# --- OPTIMISASI LANJUTAN ---
# 1. Pra-unduh model EasyOCR agar startup aplikasi lebih cepat.
RUN python -c "import easyocr; reader = easyocr.Reader(['en', 'id'], gpu=False); print('Models downloaded successfully')"

# 2. Pembersihan agresif untuk mengurangi ukuran layer virtual environment.
RUN find /opt/venv -name "*.pyc" -delete && \
    find /opt/venv -name "__pycache__" -type d -exec rm -rf {} + && \
    find /opt/venv/lib/python3.10/site-packages/torch/test -type d -exec rm -rf {} + && \
    find /opt/venv/lib/python3.10/site-packages/torchvision/test -type d -exec rm -rf {} +


# =================== STAGE 2: PRODUCTION ===================
# Tahap ini fokus untuk menciptakan image final yang ramping dan aman.
FROM python:3.10-slim-bullseye AS production

# Variabel lingkungan untuk produksi
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_ENV=production

# Menginstal HANYA dependensi sistem yang dibutuhkan saat runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Menyalin virtual environment yang sudah jadi dari tahap builder
COPY --from=builder /opt/venv /opt/venv

# Membuat user non-root untuk keamanan (praktik terbaik)
RUN useradd --system --create-home appuser
USER appuser

# Menetapkan direktori kerja untuk aplikasi
WORKDIR /home/appuser/app

# Menyalin kode aplikasi
COPY --chown=appuser:appuser ./app .

# Mengekspos port aplikasi
EXPOSE 5000

# Perintah untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]