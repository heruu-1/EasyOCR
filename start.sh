#!/bin/bash
echo "Starting EasyOCR Application..."
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --worker-class sync app.app:app
