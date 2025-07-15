#!/bin/bash
echo "🚀 Starting EasyOCR Application..."
echo "🐍 Python version: $(python --version)"
echo "💾 Available memory: $(free -h | awk '/^Mem:/ {print $7}')"
echo "🔧 Installing dependencies..."
pip install -r requirements.txt
echo "📦 Dependencies installed successfully"
echo "🌐 Starting application on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --worker-connections 10 --max-requests 100 --max-requests-jitter 10 --timeout 300 --keep-alive 5 --preload app.app:app
