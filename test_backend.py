import requests
import json

# Test the backend endpoints on Vercel
base_url = "https://etl-dashboard-io3bltzze-storbiics-projects.vercel.app"

def test_endpoint(endpoint, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}")
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"\n{method} {endpoint}")
        print(f"Error: {str(e)}")
        return False

# Test all endpoints
print("Testing backend endpoints on Vercel...")

# Test profile endpoint
test_endpoint("/api/profile", "POST", {"file_id": "test", "sheet_name": "Sheet1"})

# Test transform endpoint  
test_endpoint("/api/transform", "POST", {"file_id": "test"})

# Test preview endpoint
test_endpoint("/api/preview", "POST", {"file_id": "test", "sheet_name": "Sheet1"})

print("\nBackend endpoint tests completed!")