"""
Script to test the teleconsultation API.
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

# Test getting teleconsultations as a doctor
def test_doctor_teleconsults():
    token = login_as_doctor()
    print(f"Doctor token: {token}")
    
    response = requests.get(
        f"{BASE_URL}/doctors/teleconsults/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Response text: {response.text}")

# Test getting teleconsultations as a patient
def test_patient_teleconsults():
    token = login_as_patient()
    print(f"Patient token: {token}")
    
    response = requests.get(
        f"{BASE_URL}/doctors/teleconsults/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Response text: {response.text}")

# Run the tests
if __name__ == "__main__":
    print("Testing as doctor:")
    test_doctor_teleconsults()
    
    print("\nTesting as patient:")
    test_patient_teleconsults()
