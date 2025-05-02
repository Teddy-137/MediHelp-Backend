"""
Script to load clinic data from fixtures.
Run this script using:
python load_clinic_data.py
"""

import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medihelp.settings')
django.setup()

from django.core.management import call_command

def load_clinic_data():
    """Load clinic data from fixtures."""
    try:
        # First, check if there are any existing clinics
        from clinics.models import Clinic
        existing_count = Clinic.objects.count()
        print(f"Found {existing_count} existing clinics in the database.")
        
        # Load the fixture data
        print("Loading clinic data from fixtures...")
        call_command('loaddata', 'clinics/fixtures/initial_data.json', verbosity=2)
        
        # Verify the data was loaded
        new_count = Clinic.objects.count()
        print(f"Successfully loaded {new_count - existing_count} new clinics.")
        print(f"Total clinics in database: {new_count}")
        
        # Print some sample data
        print("\nSample clinics:")
        for clinic in Clinic.objects.all()[:3]:
            print(f"- {clinic.name} ({clinic.address})")
            if clinic.location:
                print(f"  Location: {clinic.location.x}, {clinic.location.y}")
            print(f"  Phone: {clinic.phone}")
            print(f"  Opening Hours: {clinic.opening_hours}")
            print()
            
        return True
    except Exception as e:
        print(f"Error loading clinic data: {e}")
        return False

if __name__ == "__main__":
    success = load_clinic_data()
    sys.exit(0 if success else 1)
