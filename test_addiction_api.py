"""
Quick test script for addiction insights API
Run: python test_addiction_api.py
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def test_addiction_endpoint():
    print("🧪 Testing Addiction Insights API\n")
    print("="*60)
    
    # Test endpoint
    user_id = "test_user"
    url = f"{BASE_URL}/addiction-insights/{user_id}"
    
    print(f"Testing: {url}")
    print("-"*60)
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Response:")
            print(json.dumps(data, indent=2))
            
            if data.get('status') == 'success':
                print("\n📊 Parsed Results:")
                print(f"Risk Level: {data['risk_assessment']['label']} ({data['risk_assessment']['level']}/3)")
                print(f"Confidence: {data['risk_assessment']['probability']*100:.1f}%")
                print(f"Insights: {len(data['insights'])} found")
                print(f"Recommendations: {len(data['recommendations'])} provided")
                print(f"Trend: {data['trend']['direction']}")
                print("\n✅ API is working correctly!")
            else:
                print(f"\n⚠️  Status: {data.get('status')}")
                print(f"Message: {data.get('message')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the ML backend is running:")
        print("  cd d:\\work\\mlmodel")
        print("  python start_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_addiction_endpoint()
