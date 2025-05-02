"""
Script to test minimal update of availability.
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8001/api"

# Login as a doctor
def login_as_doctor():
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "neuro@example.com", "password": "NeuroPass456!"}
    )
    data = response.json()
    return data["tokens"]["access"]

# Test updating an availability slot with minimal data
def test_minimal_update():
    token = login_as_doctor()
    
    # Get the first availability slot
    response = requests.get(
        f"{BASE_URL}/doctors/availability/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    availabilities = response.json()
    if not availabilities:
        print("No availabilities found")
        return
        
    availability_id = availabilities[0]["id"]
    
    # Update only the end_time
    response = requests.patch(
        f"{BASE_URL}/doctors/availability/{availability_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "end_time": "13:00:00"
        }
    )
    
    print(f"Update status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Update response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Update response text: {response.text}")

# Run the test
if __name__ == "__main__":
    print("Testing minimal update (end_time only):")
    test_minimal_update()
