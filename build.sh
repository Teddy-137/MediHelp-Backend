#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load initial fixture data
echo "Loading initial data fixtures..."

# Load symptoms first (other apps may depend on it)
if [ -f "symptoms/fixtures/initial_data.json" ]; then
    echo "Loading symptoms initial data..."
    python manage.py loaddata symptoms/fixtures/initial_data.json
else
    echo "Warning: symptoms fixtures not found"
fi

# Load education fixtures
if [ -f "education/fixtures/initial_data.json" ]; then
    echo "Loading education initial data..."
    python manage.py loaddata education/fixtures/initial_data.json
else
    echo "Warning: education fixtures not found"
fi

# Load firstaid fixtures
if [ -f "firstaid/fixtures/initial_data.json" ]; then
    echo "Loading firstaid initial data..."
    python manage.py loaddata firstaid/fixtures/initial_data.json
else
    echo "Warning: firstaid fixtures not found"
fi

# Load doctors fixtures if they exist and have content
# Check both possible filenames (initial_data.json and inital_data.json for typo compatibility)
if [ -s "doctors/fixtures/initial_data.json" ]; then
    echo "Loading doctors initial data..."
    python manage.py loaddata doctors/fixtures/initial_data.json
elif [ -s "doctors/fixtures/inital_data.json" ]; then
    echo "Loading doctors initial data (from inital_data.json)..."
    python manage.py loaddata doctors/fixtures/inital_data.json
else
    echo "Skipping doctors fixtures (empty or not found)"
fi

echo "Initial data loading completed!"

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
