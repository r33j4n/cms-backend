import requests
import json

# Test flat owner login
def test_login():
    # Base URL - adjust if your server is running on a different port
    base_url = "http://localhost:5000"
    
    # Test data - replace with valid flat number and PIN
    login_data = {
        "flat_no": "101",  # Replace with a valid flat number from your database
        "pin_no": "1234"   # Replace with the corresponding PIN
    }
    
    # Make the login request
    response = requests.post(f"{base_url}/api/login", json=login_data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check if login was successful
    if response.status_code == 200 and response.json().get('success'):
        print("Login successful!")
    else:
        print("Login failed!")

if __name__ == "__main__":
    test_login()