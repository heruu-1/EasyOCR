# Dockerfile untuk EasyOCR Bukti Setor
# ==============================================================================

# Gunakan base image Python official (slim biar ringan)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies OS penting: Tesseract OCR, Poppler (buat convert PDF), dan lib yang dibutuhin OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ind \
    poppler-utils \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libfontconfig1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory di container
WORKDIR /app

# Copy requirements.txt dulu (buat cache layer)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code ke container
COPY . .

# Buat folder upload
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Jalankan app dengan gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--workers=2", "--timeout=300"]
