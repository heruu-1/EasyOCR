# TROUBLESHOOTING_FRONTEND_CONNECTION.md

## 🎉 STATUS UPDATE: CONNECTION SUCCESSFUL!

**Latest Status:** Frontend berhasil connect ke backend Railway! ✅

```
Log Evidence:
[2025-07-15 07:52:01] Starting gunicorn 21.2.0
[2025-07-15 07:52:01] Listening at: http://0.0.0.0:8000
🚀 Route /api/bukti_setor/process terpanggil (2x)
```

**Conclusion:** Problem solved! Frontend-backend integration working correctly.

---

## 🔧 Troubleshooting Frontend Connection Issues

Panduan lengkap untuk mengatasi masalah koneksi antara frontend Vercel dan backend Railway.

### 🔍 Identifikasi Masalah

#### 1. Cek Environment Variable Frontend

Frontend memerlukan environment variable `REACT_APP_EASYOCR_API` untuk endpoint bukti setor.

**Di Vercel Dashboard:**

1. Masuk ke project `proyek-pajak`
2. Settings > Environment Variables
3. Pastikan ada: `REACT_APP_EASYOCR_API = https://your-railway-app.railway.app`

#### 2. Cek URL Railway Backend

```bash
# Cara mendapatkan URL Railway:
railway status
# atau lihat di Railway dashboard
```

#### 3. Test Endpoint Secara Manual

**Test basic connectivity:**

```bash
# Ganti YOUR_RAILWAY_URL dengan URL aktual
curl https://YOUR_RAILWAY_URL/health

# Test CORS
curl -H "Origin: https://proyek-pajak.vercel.app" \
     https://YOUR_RAILWAY_URL/test-cors
```

### 🛠️ Langkah-langkah Perbaikan

#### Langkah 1: Update Environment Variable di Vercel

1. **Masuk ke Vercel Dashboard**

   - Login ke https://vercel.com
   - Pilih project `proyek-pajak`

2. **Update Environment Variables**

   ```
   Settings > Environment Variables

   Add/Update:
   Name: REACT_APP_EASYOCR_API
   Value: https://your-actual-railway-url.railway.app
   Environment: Production
   ```

3. **Redeploy Frontend**
   ```bash
   # Trigger redeploy di Vercel
   # Atau push commit baru ke GitHub
   ```

#### Langkah 2: Test Backend Railway

1. **Cek Backend Status**

   ```bash
   # Test endpoint
   https://your-railway-url.railway.app/health
   ```

2. **Expected Response:**
   ```json
   {
     "status": "healthy",
     "service": "EasyOCR Bukti Setor",
     "cors_enabled": true,
     "endpoints": [
       "/api/bukti_setor/process",
       "/api/bukti_setor/save",
       "/api/bukti_setor/history"
     ]
   }
   ```

#### Langkah 3: Test CORS

1. **Test di Browser Console**

   ```javascript
   // Buka https://proyek-pajak.vercel.app/bukti-setor
   // Di browser console, jalankan:

   fetch("https://your-railway-url.railway.app/test-cors", {
     method: "GET",
     headers: {
       Origin: "https://proyek-pajak.vercel.app",
     },
   })
     .then((r) => r.json())
     .then((data) => console.log("CORS Test:", data))
     .catch((err) => console.error("CORS Error:", err));
   ```

2. **Expected Response:**
   ```json
   {
     "message": "CORS test successful",
     "method": "GET",
     "origin": "https://proyek-pajak.vercel.app"
   }
   ```

### 🔍 Debugging Network Issues

#### 1. Browser Developer Tools

```javascript
// Di browser, buka Network tab
// Upload file di https://proyek-pajak.vercel.app/bukti-setor
// Lihat request yang gagal

// Check:
// - Request URL: apakah menuju Railway?
// - Status Code: 200 OK atau error?
// - Response Headers: ada Access-Control-Allow-Origin?
// - Console Errors: ada CORS error?
```

#### 2. Common Error Messages

**CORS Error:**

```
Access to fetch at 'https://railway-url' from origin 'https://proyek-pajak.vercel.app'
has been blocked by CORS policy
```

**Solution:** Update CORS configuration di backend.

**Network Error:**

```
TypeError: Failed to fetch
```

**Solution:** Check Railway URL dan pastikan backend online.

**404 Not Found:**

```
POST https://railway-url/api/bukti_setor/process 404
```

**Solution:** Check endpoint routing di backend.

### 📝 Environment Variable Template

**File: `.env` (untuk local development)**

```bash
# Replace with your actual Railway URL
REACT_APP_EASYOCR_API=https://easyocr-production-xxxx.railway.app
REACT_APP_API_URL=https://your-main-backend.railway.app
REACT_APP_TESSERACT_API=https://your-tesseract-backend.railway.app
```

**Vercel Environment Variables:**

```
REACT_APP_EASYOCR_API = https://easyocr-production-xxxx.railway.app
REACT_APP_API_URL = https://your-main-backend.railway.app
REACT_APP_TESSERACT_API = https://your-tesseract-backend.railway.app
```

### ✅ Verification Checklist

- [ ] Railway backend online dan accessible
- [ ] Environment variable `REACT_APP_EASYOCR_API` set di Vercel
- [ ] Frontend redeploy setelah environment variable update
- [ ] CORS test berhasil
- [ ] Network tab browser tidak show CORS error
- [ ] Backend logs show incoming requests

### 🎯 Quick Fix Commands

```bash
# 1. Check Railway status
railway status

# 2. Test Railway endpoint
curl https://your-railway-url.railway.app/health

# 3. Check frontend build logs
# Di Vercel dashboard > Deployments > View Build Logs

# 4. Test full workflow
# Buka https://proyek-pajak.vercel.app/bukti-setor
# Upload file dan lihat Network tab
```

### 🆘 Jika Masih Bermasalah

1. **Share Railway URL** yang aktual
2. **Share Vercel Environment Variables** screenshot
3. **Share Browser Console Errors**
4. **Share Network Tab** request details

Dengan informasi ini, bisa debugging lebih spesifik!
