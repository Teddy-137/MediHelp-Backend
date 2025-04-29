from django.db import models
from .validators import validate_json_array
from symptoms.models import Condition


class FirstAidInstruction(models.Model):
    class SeverityLevel(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    title = models.CharField(
        max_length=200, help_text="Short title for the instruction"
    )
    steps = models.JSONField(
        help_text="JSON array of steps e.g., ['Step 1', 'Step 2']",
        validators=[validate_json_array], 
    )
    description = models.TextField(null=True, blank=True)
    condition = models.ForeignKey("symptoms.Condition", on_delete=models.CASCADE)
    severity_level = models.PositiveSmallIntegerField(
        choices=SeverityLevel.choices, default=SeverityLevel.LOW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class HomeRemedy(models.Model):
    name = models.CharField(max_length=200)
    symptoms = models.ManyToManyField("symptoms.Symptom")
    ingredients = models.JSONField(
        help_text="JSON array of ingredients e.g., ['Honey', 'Lemon']",
        validators=[validate_json_array],
    )
    preparation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
