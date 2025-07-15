# EasyOCR Production Deployment Guide

## 🚀 Optimizations Implemented

### Memory Management

- Lazy loading EasyOCR (initialize on first use)
- Aggressive garbage collection after processing
- Image size optimization (max 800px width, 1000px height)
- Limited PDF pages (max 10 pages)
- Memory cleanup after each page processing

### Performance Enhancements

- Single worker with optimized connections
- Request recycling (max 100 requests per worker)
- Reduced DPI for PDF conversion (150 DPI)
- Preloading application for faster startup
- Connection keepalive for better performance

### Error Handling & Monitoring

- Comprehensive health checks (`/health` and `/health/deep`)
- System resource monitoring with psutil
- Better error messages and logging
- Graceful fallback for failed pages
- Request timeout handling (300s)

### Docker Optimizations

- Multi-stage virtual environment
- Optimized system dependencies
- Environment variables for threading control
- Memory arena optimization
- Clean package cache

## 📊 Resource Usage

- **Memory**: Optimized for 512MB-1GB containers
- **CPU**: Single-threaded with controlled OpenMP threads
- **Storage**: Minimal with automatic cleanup
- **Network**: Keepalive connections for efficiency

## 🔧 Configuration Variables

### Required Environment Variables

```
PORT=8000
FLASK_ENV=production
UPLOAD_FOLDER=uploads
```

### Optional Optimization Variables

```
MAX_PAGES_PER_PDF=10
OCR_DPI=150
MAX_IMAGE_SIZE=800
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=10485760
OMP_NUM_THREADS=1
```

## 🏥 Health Check Endpoints

- `GET /` - Basic service status
- `GET /health` - Comprehensive health with system metrics
- `GET /health/deep` - OCR engine and dependencies check

## 📈 Performance Expectations

- **Startup Time**: 30-60 seconds (OCR model loading)
- **Processing Time**: 5-15 seconds per page
- **Memory Usage**: 200-500MB during processing
- **Max File Size**: 10MB
- **Max Pages**: 10 pages per PDF

## 🚨 Troubleshooting

### Common Issues

1. **Memory errors**: Reduce MAX_IMAGE_SIZE or MAX_PAGES_PER_PDF
2. **Timeout errors**: Increase gunicorn timeout
3. **OCR failures**: Check `/health/deep` endpoint
4. **Startup delays**: Normal for first-time model download

### Monitoring Commands

```bash
# Check health
curl https://your-app.railway.app/health

# Deep health check
curl https://your-app.railway.app/health/deep

# Test OCR endpoint
curl -X POST -F "file=@test.pdf" https://your-app.railway.app/api/bukti_setor/process
```

## 🔄 Deployment Process

1. **Build**: Railway builds Docker image with optimizations
2. **Deploy**: Single worker starts with preloaded app
3. **Initialize**: OCR engine loads on first request (lazy loading)
4. **Monitor**: Health checks provide system status
5. **Scale**: Auto-restart on failures (max 3 retries)

## 📝 Logs to Monitor

- `📦 EasyOCR module loaded` - Module import successful
- `🔄 Memulai inisialisasi EasyOCR Reader` - OCR initialization
- `✅ EasyOCR Reader berhasil diinisialisasi` - OCR ready
- `🚀 Starting processing for file` - Request processing
- `✅ Page X processed in Xs` - Successful processing
- `🎉 Processing completed` - Full request complete
