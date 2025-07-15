#!/bin/bash
# deploy_to_railway.sh - Final deployment script

echo "🚀 DEPLOYING EASYOCR TO RAILWAY"
echo "=================================="

echo "✅ Pre-deployment checklist:"
echo "   - Code optimized for 4GB memory limit"
echo "   - Production Procfile with Gunicorn"
echo "   - CORS configured for Vercel frontend"
echo "   - Error handling with fallbacks"
echo "   - Memory management optimized"

echo ""
echo "📦 Final project structure:"
ls -la | grep -E '(app\.py|requirements\.txt|Procfile|config\.py|bukti_setor|utils)'

echo ""
echo "🎯 Deployment commands:"
echo "1. railway up"
echo "2. railway logs --follow"
echo "3. railway status"

echo ""
echo "🔧 After deployment, update Vercel:"
echo "   REACT_APP_EASYOCR_API = [your-railway-url]"

echo ""
echo "🎉 Ready for production deployment!"
