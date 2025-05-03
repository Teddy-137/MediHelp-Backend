#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Create superuser if it doesn't exist
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
email = "${DJANGO_SUPERUSER_EMAIL}"
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        first_name="${DJANGO_SUPERUSER_FIRST_NAME}",
        last_name="${DJANGO_SUPERUSER_LAST_NAME}",
        phone="${DJANGO_SUPERUSER_PHONE}",
        password="${DJANGO_SUPERUSER_PASSWORD}"
    )
EOF
