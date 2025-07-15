#!/bin/bash
echo "🚀 Starting EasyOCR Application..."
echo "🐍 Python version: $(python --version)"
echo "💾 Available memory: $(free -h | awk '/^Mem:/ {print $7}')"
echo "🔧 Installing dependencies..."
pip install -r requirements.txt
echo "📦 Dependencies installed successfully"
echo "🌐 Starting application on port $PORT"
exec gunicorn -b 0.0.0.0:$PORT app.app:app
