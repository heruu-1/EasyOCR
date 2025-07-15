#!/usr/bin/env python3
# test_app.py - Script untuk test aplikasi EasyOCR Bukti Setor

import sys
import os
import requests
from pathlib import Path

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check berhasil")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check gagal: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to app: {e}")
        return False

def test_main_endpoint():
    """Test main endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Main endpoint berhasil")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Main endpoint gagal: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to main endpoint: {e}")
        return False

def main():
    print("🚀 Testing EasyOCR Bukti Setor Application")
    print("=" * 50)
    
    # Test endpoints
    health_ok = test_health_endpoint()
    main_ok = test_main_endpoint()
    
    print("\n" + "=" * 50)
    if health_ok and main_ok:
        print("✅ Semua test berhasil!")
        print("📝 Aplikasi siap untuk digunakan")
        print("🌐 Akses: http://localhost:8000")
    else:
        print("❌ Beberapa test gagal")
        print("💡 Pastikan aplikasi sudah berjalan dengan: python app.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
