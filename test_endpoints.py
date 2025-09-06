import requests

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {endpoint} endpoint is working!")
            print(response.json())
        else:
            print(f"❌ {endpoint} endpoint returned status code {response.status_code}")
    except Exception as e:
        print(f"❌ Could not reach {endpoint} endpoint. Error: {e}")

if __name__ == "__main__":
    test_endpoint("users")
    print("\n")
    test_endpoint("products")
