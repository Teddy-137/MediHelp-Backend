"""
Script to test the availability API.
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8001/api"


# Login as a doctor
def login_as_doctor():
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "neuro@example.com", "password": "NeuroPass456!"},
    )
    data = response.json()
    return data["tokens"]["access"]


# Test creating an availability slot
def test_create_availability():
    token = login_as_doctor()
    print(f"Doctor token: {token}")

    # Create a new availability slot for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    response = requests.post(
        f"{BASE_URL}/doctors/availability/",
        headers={"Authorization": f"Bearer {token}"},
        json={"day": tomorrow, "start_time": "10:00:00", "end_time": "12:00:00"},
    )

    print(f"Create status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Create response data: {json.dumps(data, indent=2)}")
        return data.get("id")
    except:
        print(f"Create response text: {response.text}")
        return None


# Test getting all availability slots
def test_get_availabilities():
    token = login_as_doctor()

    response = requests.get(
        f"{BASE_URL}/doctors/availability/",
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"List status code: {response.status_code}")
    try:
        data = response.json()
        print(f"List response data: {json.dumps(data, indent=2)}")
    except:
        print(f"List response text: {response.text}")


# Test updating an availability slot
def test_update_availability(availability_id):
    if not availability_id:
        print("No availability ID provided for update test")
        return

    token = login_as_doctor()

    response = requests.patch(
        f"{BASE_URL}/doctors/availability/{availability_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"start_time": "10:30:00", "end_time": "12:30:00"},
    )

    print(f"Update status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Update response data: {json.dumps(data, indent=2)}")
    except:
        print(f"Update response text: {response.text}")


# Run the tests
if __name__ == "__main__":
    print("Testing availability creation:")
    availability_id = test_create_availability()

    print("\nTesting availability listing:")
    test_get_availabilities()

    if availability_id:
        print("\nTesting availability update:")
        test_update_availability(availability_id)
