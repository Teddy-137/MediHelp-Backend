"""
Script to test updating teleconsultation status.
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

# Login as a doctor
def login_as_doctor():
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "neuro@example.com", "password": "NeuroPass456!"}
    )
    data = response.json()
    return data["tokens"]["access"]

# Login as a patient
def login_as_patient():
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "test@example.com", "password": "TestPassword123!"}
    )
    data = response.json()
    return data["tokens"]["access"]

# Test updating teleconsultation status as a doctor
def test_doctor_update_status():
    token = login_as_doctor()
    print(f"Doctor token: {token}")
    
    # Get teleconsultations for this doctor
    response = requests.get(
        f"{BASE_URL}/doctors/teleconsults/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    teleconsults = response.json()
    if not teleconsults:
        print("No teleconsultations found for this doctor")
        return
        
    teleconsult_id = teleconsults[0]["id"]
    
    # Update the status to completed
    response = requests.patch(
        f"{BASE_URL}/doctors/teleconsults/{teleconsult_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "status": "completed"
        }
    )
    
    print(f"Update status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Update response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Update response text: {response.text}")
        
    # Try with an invalid status
    response = requests.patch(
        f"{BASE_URL}/doctors/teleconsults/{teleconsult_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "status": "invalid_status"
        }
    )
    
    print(f"\nInvalid status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Invalid status response: {json.dumps(data, indent=2)}")
    except:
        print(f"Invalid status response text: {response.text}")

# Test updating teleconsultation status as a patient
def test_patient_update_status():
    token = login_as_patient()
    print(f"\nPatient token: {token}")
    
    # Get teleconsultations for this patient
    response = requests.get(
        f"{BASE_URL}/doctors/teleconsults/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    teleconsults = response.json()
    if not teleconsults:
        print("No teleconsultations found for this patient")
        return
        
    teleconsult_id = teleconsults[0]["id"]
    
    # Update the status to cancelled
    response = requests.patch(
        f"{BASE_URL}/doctors/teleconsults/{teleconsult_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "status": "cancelled"
        }
    )
    
    print(f"Update status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Update response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Update response text: {response.text}")

# Run the tests
if __name__ == "__main__":
    print("Testing teleconsultation status update as doctor:")
    test_doctor_update_status()
    
    print("\nTesting teleconsultation status update as patient:")
    test_patient_update_status()
