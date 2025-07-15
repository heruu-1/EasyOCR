# frontend_env_setup.md - Panduan konfigurasi environment variable untuk frontend

## Environment Variables yang Diperlukan Frontend

Frontend memerlukan beberapa environment variable untuk connect ke backend Railway:

### File: `.env` (di folder frontend)

```bash
# API URLs - sesuaikan dengan deployment Anda
REACT_APP_API_URL=https://your-railway-app.railway.app
REACT_APP_TESSERACT_API=https://your-tesseract-backend.railway.app
REACT_APP_EASYOCR_API=https://your-easyocr-backend.railway.app
```

### Penjelasan:

1. **REACT_APP_API_URL**: URL utama untuk backend faktur (jika ada)
2. **REACT_APP_TESSERACT_API**: URL untuk backend Tesseract OCR (untuk faktur)
3. **REACT_APP_EASYOCR_API**: URL untuk backend EasyOCR (untuk bukti setor) ← **INI YANG PENTING**

### Dari analisis kode frontend GitHub:

```javascript
// File: frontend/src/services/api.js
const API_URL = process.env.REACT_APP_API_URL;
const TESSERACT_API = process.env.REACT_APP_TESSERACT_API;
const EASYOCR_API = process.env.REACT_APP_EASYOCR_API;

// Bukti Setor menggunakan EASYOCR_API
export const processBuktiSetor = (formData) =>
  easyOCRApiForm.post("/api/bukti_setor/process", formData);
```

### Langkah-langkah Fixing:

1. **Dapatkan URL Railway Anda:**

   ```bash
   railway status
   # atau cek di Railway dashboard
   ```

2. **Update environment variable di Vercel:**

   - Masuk ke Vercel dashboard
   - Pilih project proyek-pajak
   - Settings > Environment Variables
   - Add/Update:
     ```
     REACT_APP_EASYOCR_API = https://your-railway-app.railway.app
     ```

3. **Redeploy frontend di Vercel:**
   ```bash
   # Trigger redeploy agar environment variable baru aktif
   ```

### Testing Koneksi:

Setelah setup, test endpoint ini di browser:

```
https://proyek-pajak.vercel.app/bukti-setor
```

Dan pastikan di Network tab browser, request POST ke:

```
https://your-railway-app.railway.app/api/bukti_setor/process
```

### Debugging:

Jika masih error, cek:

1. CORS headers di Railway response
2. Network tab di browser untuk melihat actual request URL
3. Console log di browser untuk error message
4. Railway logs untuk melihat apakah request sampai ke backend

### URL Railway Contoh:

```
https://easyocr-production-xxxx.railway.app
```

(Ganti xxxx dengan actual deployment ID Anda)
