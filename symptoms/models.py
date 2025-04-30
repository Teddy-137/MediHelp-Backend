from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Condition(models.Model):
    class SeverityChoices(models.IntegerChoices):
        MILD = 1, "Mild"
        MODERATE = 2, "Moderate"
        SEVERE = 3, "Severe"

    name = models.CharField(max_length=100, unique=True)
    severity = models.PositiveSmallIntegerField(
        choices=SeverityChoices.choices, default=SeverityChoices.MILD
    )
    description = models.TextField()
    symptoms = models.ManyToManyField(Symptom, through="SymptomCondition")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SymptomCondition(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField(default=5)

    class Meta:
        unique_together = ("symptom", "condition")


class SymptomCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom)
    conditions = models.ManyToManyField(Condition, blank=True)
    ai_diagnosis = models.JSONField(null=True, blank=True)  # Gemini API response
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s check at {self.created_at:%Y-%m-%d %H:%M}"
