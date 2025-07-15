#!/bin/bash
# upgrade_to_full_ocr.sh - Script untuk upgrade dari simple app ke full OCR

echo "🔄 Upgrading to Full OCR deployment..."

# Backup current configs
cp nixpacks.toml nixpacks.simple.toml.bak
cp Procfile Procfile.simple.bak

# Update nixpacks.toml untuk full OCR
cat > nixpacks.toml << 'EOF'
[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT app:app --workers=2 --timeout=300"

[phases.setup]
nixPkgs = ["python39", "tesseract", "poppler_utils"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[variables]
PYTHONPATH = "/app"
FLASK_ENV = "production"
EOF

# Update Procfile untuk full OCR
cat > Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:$PORT app:app --workers=2 --timeout=300
EOF

echo "✅ Configuration updated for full OCR"
echo "📤 Ready to commit and push for redeployment"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Upgrade to full OCR'"
echo "3. git push"
echo "4. Check Railway deployment logs"
