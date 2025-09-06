import requests

BASE_URL = "http://127.0.0.1:5000"

# Test home
response = requests.get(f"{BASE_URL}/")
print("Home endpoint:")
print(response.text)
print("-" * 40)

# Test users
response = requests.get(f"{BASE_URL}/users")
print("Users endpoint:")
try:
    print(response.json())
except Exception as e:
    print("Error:", e)
print("-" * 40)

# Test products
response = requests.get(f"{BASE_URL}/products")
print("Products endpoint:")
try:
    print(response.json())
except Exception as e:
    print("Error:", e)
print("-" * 40)
