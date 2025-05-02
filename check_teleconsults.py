"""
Script to check teleconsultations in the database.
Run this script using:
python manage.py shell < check_teleconsults.py
"""

from doctors.models import Teleconsultation, DoctorProfile
from django.contrib.auth import get_user_model

User = get_user_model()

# Check all teleconsultations
teleconsults = Teleconsultation.objects.all()
print(f"Total teleconsultations: {teleconsults.count()}")

for tc in teleconsults:
    print(f"ID: {tc.id}")
    print(f"Patient: {tc.patient.email} (ID: {tc.patient.id})")
    print(f"Doctor: {tc.doctor.user.email} (ID: {tc.doctor.id})")
    print(f"Scheduled time: {tc.scheduled_time}")
    print(f"Status: {tc.status}")
    print(f"Duration: {tc.duration} minutes")
    print(f"Meeting URL: {tc.meeting_url}")
    print("-" * 50)

# Check doctor users
doctor_users = User.objects.filter(role='doctor')
print(f"\nTotal doctor users: {doctor_users.count()}")
for user in doctor_users:
    print(f"ID: {user.id}, Email: {user.email}")
    try:
        profile = DoctorProfile.objects.get(user=user)
        print(f"  Has profile: Yes (ID: {profile.id})")
        # Count teleconsultations for this doctor
        tc_count = Teleconsultation.objects.filter(doctor=profile).count()
        print(f"  Teleconsultations: {tc_count}")
    except DoctorProfile.DoesNotExist:
        print("  Has profile: No")
    print()
