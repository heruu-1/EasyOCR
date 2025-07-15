FROM python:3.10-slim-bullseye

# Environment variables untuk optimasi
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV MALLOC_ARENA_MAX=2
ENV PYTHONHASHSEED=random

WORKDIR /app

# Install system dependencies - minimal dan reliable untuk OpenCV dan OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    poppler-utils \
    libglib2.0-0 \
    libgcc-s1 \
    libstdc++6 \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip dengan optimasi cache
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Install PyTorch CPU version dengan optimasi
RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory dengan permissions
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Set environment variables untuk production
ENV FLASK_APP=app.app
ENV FLASK_ENV=production
ENV UPLOAD_FOLDER=/app/uploads
ENV PYTHONPATH=/app
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

# Expose port
EXPOSE 8000

# Jalankan Gunicorn (untuk production server)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.app:app"]
