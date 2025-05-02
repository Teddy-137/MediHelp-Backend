from django.db import models
from django.conf import settings


class SkinDiagnosis(models.Model):
    class DiagnosisStatus(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skin_diagnoses",
    )
    image = models.ImageField(
        upload_to="skin_diagnosis/%Y/%m/%d/", help_text="Upload image of skin condition"
    )
    diagnosis = models.JSONField(
        null=True, blank=True, help_text="Structured analysis results"
    )
    status = models.CharField(
        max_length=20,
        choices=DiagnosisStatus.choices,
        default=DiagnosisStatus.PROCESSING,
        db_index=True,  # Faster filtering
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Skin Diagnoses"

    def __str__(self):
        return f"Diagnosis #{self.id} - {self.user.email}"
