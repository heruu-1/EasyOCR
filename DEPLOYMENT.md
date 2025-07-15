# Deployment Steps untuk Railway

## Langkah 1: Deploy Simple App (Testing)

1. Pastikan file ini ada:

   - `simple_app.py`
   - `requirements-simple.txt`
   - `nixpacks.toml` (configured for simple app)
   - `Procfile` (configured for simple app)

2. Deploy ke Railway
3. Test endpoint:
   - `GET /health`
   - `GET /`
   - `POST /api/bukti_setor/process`

## Langkah 2: Upgrade ke Full OCR (Setelah simple app berhasil)

1. Update nixpacks.toml:

```toml
[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT app:app --workers=2 --timeout=300"

[phases.setup]
nixPkgs = ["python39", "tesseract", "poppler_utils"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[variables]
PYTHONPATH = "/app"
FLASK_ENV = "production"
```

2. Update Procfile:

```
web: gunicorn --bind 0.0.0.0:$PORT app:app --workers=2 --timeout=300
```

3. Redeploy

## Troubleshooting

- Jika simple app gagal: check logs dan port configuration
- Jika full OCR gagal: likely dependency issue, check Tesseract installation
- Memory issues: reduce workers or optimize image processing

## Current Status

✅ Simple app ready for deployment
⏳ Full OCR ready after simple app success
