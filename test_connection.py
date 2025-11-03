import requests
import time

print("Testing ML Server Connection...")
print("=" * 50)

# Test 1: Server health
print("\n1. Testing server health...")
try:
    start = time.time()
    response = requests.get("http://localhost:8001/docs", timeout=3)
    elapsed = time.time() - start
    print(f"[OK] Server is running (Response time: {elapsed:.2f}s)")
except Exception as e:
    print(f"[FAIL] Server not responding: {e}")
    exit(1)

# Test 2: API endpoint
print("\n2. Testing addiction insights API...")
try:
    start = time.time()
    response = requests.get("http://localhost:8001/api/addiction-insights/test_user", timeout=10)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] API working (Response time: {elapsed:.2f}s)")
        print(f"  - Risk Level: {data['risk_assessment']['label']}")
        print(f"  - Insights: {len(data['insights'])} items")
        print(f"  - Recommendations: {len(data['recommendations'])} items")
    else:
        print(f"[FAIL] API error: {response.status_code}")
except Exception as e:
    print(f"[FAIL] API failed: {e}")

# Test 3: Network IP (for Android)
print("\n3. Testing network IP (10.54.50.182:8001)...")
try:
    start = time.time()
    response = requests.get("http://10.54.50.182:8001/docs", timeout=3)
    elapsed = time.time() - start
    print(f"[OK] Network IP accessible (Response time: {elapsed:.2f}s)")
except Exception as e:
    print(f"[FAIL] Network IP not accessible: {e}")
    print("  Note: Make sure your firewall allows port 8001")

print("\n" + "=" * 50)
print("Connection test complete!")
print("\nNext steps:")
print("1. Rebuild React Native app: npx expo run:android")
print("2. Check app can reach: http://10.54.50.182:8001/api")
