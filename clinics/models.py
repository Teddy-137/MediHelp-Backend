from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
import re


def validate_opening_hours(value):
    """
    Validate that opening_hours is a dictionary with days of the week as keys
    and time ranges as values in the format "HH:MM-HH:MM".
    """
    valid_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Check if value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError("Opening hours must be a dictionary")

    # Check if keys are valid days
    for day in value.keys():
        if day not in valid_days:
            raise ValidationError(
                f"Invalid day: {day}. Must be one of {', '.join(valid_days)}"
            )

    # Check if values are valid time ranges
    time_pattern = re.compile(
        r"^([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    for day, hours in value.items():
        if not isinstance(hours, str):
            raise ValidationError(f"Hours for {day} must be a string")

        if hours.lower() == "closed":
            continue  # Allow "closed" as a valid value

        if not time_pattern.match(hours):
            raise ValidationError(
                f"Invalid time format for {day}: {hours}. "
                "Must be in the format 'HH:MM-HH:MM' or 'closed'"
            )

        # Check that start time is before end time
        start, end = hours.split("-")
        if start >= end:
            raise ValidationError(
                f"Invalid time range for {day}: {hours}. "
                "Start time must be before end time"
            )


class Clinic(models.Model):
    name = models.CharField(max_length=200)
    location = models.PointField(
        geography=True, null=True, help_text="The geographical location of the clinic"
    )
    address = models.TextField()
    phone = models.CharField(max_length=20)
    opening_hours = models.JSONField(
        default=dict,
        validators=[validate_opening_hours],
        help_text="Opening hours as a JSON object, e.g., {'Monday': '9:00-17:00'}",
    )

    def __str__(self):
        return self.name

    def clean(self):
        """
        Additional model validation.
        """
        super().clean()

        # Validate opening_hours
        if self.opening_hours:
            validate_opening_hours(self.opening_hours)

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is always run.
        """
        self.full_clean()
        super().save(*args, **kwargs)
