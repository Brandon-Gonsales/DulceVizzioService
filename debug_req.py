import urllib.request
import json

url = "http://127.0.0.1:8000/api/users"
payload = {
    "email": "debug_user_v6@example.com",
    "password": "Password123",
    "full_name": "Debug User V6",
    "role": "SUPERADMIN",
    "username": "debuguserv6"
}
headers = {
    "Content-Type": "application/json"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
