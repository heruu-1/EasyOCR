# Dockerfile — Deployment Minimalis dan Optimal untuk Railway
# ===========================================================

FROM python:3.10-slim-bullseye

# Lingkungan minimal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Direktori kerja
WORKDIR /app

# Instalasi dependensi sistem untuk OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip dan wheel
RUN pip install --no-cache-dir --upgrade pip wheel

# Salin dan install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir easyocr
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode (anggap app.py ada di root /app)
COPY . .

# Buka port (Railway akan inject PORT-nya)
EXPOSE 8000

# Jalankan server pakai env PORT → fallback ke 8000 jika tidak diset
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8000} app:app"]