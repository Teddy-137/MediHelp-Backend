"""
Script to create DoctorProfile objects for users with the 'doctor' role.
Run this script using:
python manage.py shell < create_doctor_profiles.py
"""

from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile
from decimal import Decimal
import random
import string

User = get_user_model()

# Default values for required fields
DEFAULT_CONSULTATION_FEE = Decimal('100.00')
SPECIALIZATIONS = [
    'General Medicine',
    'Cardiology',
    'Neurology',
    'Pediatrics',
    'Dermatology',
    'Orthopedics',
    'Gynecology',
    'Ophthalmology',
    'Psychiatry',
    'Oncology'
]

def generate_license_number(user):
    """Generate a unique license number based on user information"""
    # Use first letter of first name, first letter of last name, and a random string
    first_initial = user.first_name[0] if user.first_name else 'X'
    last_initial = user.last_name[0] if user.last_name else 'X'
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"MED-{first_initial}{last_initial}-{random_part}"

# Get all users with the 'doctor' role
doctor_users = User.objects.filter(role='doctor')
print(f"Found {doctor_users.count()} users with 'doctor' role")

# Create DoctorProfile for each doctor user
for user in doctor_users:
    try:
        # Check if profile already exists
        profile = DoctorProfile.objects.get(user=user)
        print(f"Profile already exists for {user.email}")
    except DoctorProfile.DoesNotExist:
        # Generate a random specialization
        specialization = random.choice(SPECIALIZATIONS)
        
        # Generate a unique license number
        license_number = generate_license_number(user)
        
        # Create the profile
        profile = DoctorProfile.objects.create(
            user=user,
            license_number=license_number,
            specialization=specialization,
            consultation_fee=DEFAULT_CONSULTATION_FEE
        )
        print(f"Created profile for {user.email} with license {license_number} and specialization {specialization}")

print("Done!")
