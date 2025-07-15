#!/usr/bin/env python3
# test_app.py - Script untuk test aplikasi EasyOCR Bukti Setor

import sys
import os
import requests
import time
from pathlib import Path

def test_endpoint(url, description):
    """Test an endpoint"""
    try:
        print(f"🔍 Testing {description}...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {description} berhasil")
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {description} gagal: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error testing {description}: {e}")
        return False

def test_local():
    """Test local deployment"""
    base_url = "http://localhost:8000"
    print(f"🧪 Testing Local Deployment: {base_url}")
    print("=" * 60)
    
    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/", "Main Endpoint"),
        (f"{base_url}/api/bukti_setor/process", "OCR Process Endpoint (GET)")
    ]
    
    results = []
    for url, desc in tests:
        results.append(test_endpoint(url, desc))
    
    return all(results)

def test_railway(app_url):
    """Test Railway deployment"""
    print(f"🚀 Testing Railway Deployment: {app_url}")
    print("=" * 60)
    
    tests = [
        (f"{app_url}/health", "Health Check"),
        (f"{app_url}/", "Main Endpoint"),
        (f"{app_url}/api/bukti_setor/process", "OCR Process Endpoint")
    ]
    
    results = []
    for url, desc in tests:
        results.append(test_endpoint(url, desc))
    
    return all(results)

def main():
    print("🚀 EasyOCR Bukti Setor - Deployment Tester")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Test Railway deployment
        app_url = sys.argv[1]
        if not app_url.startswith('http'):
            app_url = f"https://{app_url}"
        
        success = test_railway(app_url)
    else:
        # Test local deployment
        success = test_local()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Semua test berhasil!")
        print("📝 Aplikasi siap untuk digunakan")
    else:
        print("❌ Beberapa test gagal")
        print("💡 Periksa logs aplikasi untuk detail error")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Usage: python {os.path.basename(__file__)} [railway-app-url]")
        print("Examples:")
        print(f"  python {os.path.basename(__file__)}  # Test local")
        print(f"  python {os.path.basename(__file__)} your-app.railway.app  # Test Railway")
        print()
    
    main()
