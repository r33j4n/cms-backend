import requests
import json

# Base URL - adjust if your server is running on a different port
base_url = "http://localhost:5000"

# Test flat owner registration
def test_register_flat_owner():
    # Test data
    flat_owner_data = {
        "flat_no": "102",  # Use a unique flat number
        "pin_no": "5678",
        "contact_no": "9876543210"
    }
    
    # Make the registration request
    response = requests.post(f"{base_url}/api/flat-owner", json=flat_owner_data)
    
    # Print the response
    print("\n=== Flat Owner Registration ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json().get('flat_no'), flat_owner_data['pin_no']

# Test complaint submission
def test_submit_complaint(flat_no, pin_no):
    # Test data
    complaint_data = {
        "flat_no": flat_no,
        "pin_no": pin_no,
        "complaint": "Test complaint: The water heater is not working properly."
    }
    
    # Make the complaint submission request
    response = requests.post(f"{base_url}/api/complaint", json=complaint_data)
    
    # Print the response
    print("\n=== Complaint Submission ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test getting public complaints
def test_get_complaints():
    # Make the request to get all complaints
    response = requests.get(f"{base_url}/api/complaints")
    
    # Print the response
    print("\n=== Get Public Complaints ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    # Test flat owner registration
    flat_no, pin_no = test_register_flat_owner()
    
    # Test complaint submission with the newly registered flat owner
    test_submit_complaint(flat_no, pin_no)
    
    # Test getting all complaints
    test_get_complaints()