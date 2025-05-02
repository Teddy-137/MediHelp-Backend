"""
Script to check clinics in the database.
Run this script using:
python manage.py shell < check_clinics.py
"""

from clinics.models import Clinic
import json

# Check all clinics
clinics = Clinic.objects.all()
print(f"Total clinics: {clinics.count()}")

for clinic in clinics:
    print(f"ID: {clinic.id}")
    print(f"Name: {clinic.name}")
    print(f"Address: {clinic.address}")
    print(f"Phone: {clinic.phone}")
    print(f"Opening Hours: {json.dumps(clinic.opening_hours, indent=2)}")
    if clinic.location:
        print(f"Location: Point({clinic.location.x}, {clinic.location.y})")
    else:
        print("Location: None")
    print("-" * 50)
