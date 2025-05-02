from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"dr.{self.user.first_name} {self.user.last_name}"


class Availability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor} - {self.day}"


class Teleconsultation(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="patient_consults",
        on_delete=models.CASCADE,
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        related_name="doctor_consults",
        on_delete=models.CASCADE,
    )

    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, default=Status.SCHEDULED)
    duration = models.PositiveIntegerField()
    meeting_url = models.URLField()

    class Meta:
        unique_together = ("patient", "doctor", "scheduled_time")
        ordering = ["scheduled_time"]

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.scheduled_time}"

    def clean(self):
        if self.scheduled_time < timezone.now():
            raise ValidationError("Cannot schedule consultation in the past")

        if not 15 <= self.duration <= 180:
            raise ValidationError("Duration must be between 15 and 180 minutes")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
