import requests
import json

# Base URL - adjust if your server is running on a different port
base_url = "http://localhost:5000"

def test_admin_login():
    """Test admin login to get authentication token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/api/auth/admin/login", json=login_data)
    
    print("\n=== Admin Login ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Return the token for use in subsequent requests
    return response.json().get('token')

def test_dashboard_stats(token):
    """Test the dashboard stats endpoint"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{base_url}/api/admin/dashboard-stats", headers=headers)
    
    print("\n=== Dashboard Stats ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    # Login as admin to get token
    token = test_admin_login()
    
    if token:
        # Test dashboard stats endpoint
        test_dashboard_stats(token)
    else:
        print("Failed to get authentication token. Cannot test dashboard stats.")