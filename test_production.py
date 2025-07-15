#!/usr/bin/env python3
# test_production_api.py - Quick test for production API

import requests
import json
import time

def test_api_endpoints():
    """Test production API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Production API Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: CORS preflight
    try:
        response = requests.options(
            f"{base_url}/api/bukti_setor/process",
            headers={
                "Origin": "https://proyek-pajak.vercel.app",
                "Access-Control-Request-Method": "POST"
            },
            timeout=5
        )
        if response.status_code == 200:
            print("✅ CORS preflight: OK")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS preflight error: {e}")
    
    print("\n🎯 Production API Test Complete!")

if __name__ == "__main__":
    print("📝 Instructions:")
    print("1. Run 'python app.py' in another terminal")
    print("2. Wait for server to start")
    print("3. Run this test script")
    print("\nStarting test in 3 seconds...")
    time.sleep(3)
    test_api_endpoints()
