# test_api_connection.py - Test koneksi ke API

import requests
import json
import os

# Railway URL - ganti dengan URL Railway yang aktual
RAILWAY_URL = "https://your-railway-app.railway.app"  # Sesuaikan dengan URL Railway Anda
VERCEL_FRONTEND = "https://proyek-pajak.vercel.app"

def test_endpoint(url, method="GET", data=None):
    """Test endpoint dengan berbagai method"""
    print(f"\n🔍 Testing {method} {url}")
    
    headers = {
        "Content-Type": "application/json",
        "Origin": VERCEL_FRONTEND  # Simulasi request dari frontend
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers, timeout=10)
            
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"   Response: {response.json()}")
        else:
            print(f"   Response: {response.text[:200]}")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing API Connection to Railway Backend")
    print(f"Railway URL: {RAILWAY_URL}")
    print(f"Frontend URL: {VERCEL_FRONTEND}")
    
    # Test basic endpoints
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/test-cors", "GET"),
        ("/test-cors", "OPTIONS"),
        ("/api/bukti_setor/process", "OPTIONS"),
        ("/api/bukti_setor/save", "OPTIONS"),
        ("/api/bukti_setor/history", "GET"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        url = RAILWAY_URL + endpoint
        success = test_endpoint(url, method)
        results.append((endpoint, method, success))
    
    # Test POST endpoints dengan sample data
    print("\n🔄 Testing POST endpoints with sample data")
    
    # Test save endpoint
    sample_data = {
        "kode_setor": "411211",
        "tanggal": "2024-01-15", 
        "jumlah": 1500000
    }
    
    save_success = test_endpoint(
        RAILWAY_URL + "/api/bukti_setor/save", 
        "POST", 
        sample_data
    )
    results.append(("/api/bukti_setor/save", "POST", save_success))
    
    # Summary
    print("\n📊 Test Results Summary:")
    passed = 0
    total = len(results)
    
    for endpoint, method, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {method} {endpoint}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend should be able to connect.")
    else:
        print("⚠️ Some tests failed. Check Railway deployment and CORS configuration.")

if __name__ == "__main__":
    print("📝 Please update RAILWAY_URL variable with your actual Railway app URL")
    print("   Example: https://your-app-name.railway.app")
    print("   Then run this script again.")
    
    # Uncomment the line below after updating RAILWAY_URL
    # main()
