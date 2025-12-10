import requests
import json

def test_api():
    base_url = "http://localhost:8000/api"
    
    try:
        # Test customers endpoint
        print("Testing customers endpoint...")
        response = requests.get(f"{base_url}/customers/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Customers API working - Found {len(data)} customers")
        else:
            print(f"❌ Customers API failed - Status: {response.status_code}")
        
        # Test products endpoint
        print("Testing products endpoint...")
        response = requests.get(f"{base_url}/products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products API working - Found {len(data)} products")
        else:
            print(f"❌ Products API failed - Status: {response.status_code}")
        
        # Test orders endpoint
        print("Testing orders endpoint...")
        response = requests.get(f"{base_url}/orders/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Orders API working - Found {len(data)} orders")
        else:
            print(f"❌ Orders API failed - Status: {response.status_code}")
        
        print("\n🎉 API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api()





