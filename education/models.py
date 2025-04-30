from django.db import models
from symptoms.models import Condition, Symptom
from .validators import validate_string_list, validate_youtube_url


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(PublishableModel):
    title = models.CharField(max_length=200)
    summary = models.CharField(
        max_length=150, blank=True, help_text="Short preview text (max 150 chars)"
    )
    content = models.TextField()
    related_conditions = models.ManyToManyField(Condition, blank=True)
    tags = models.JSONField(
        blank=True,
        default=list,
        help_text="Comma-separated list of tags",
        validators=[validate_string_list],
    )
    cover_image = models.URLField(
        blank=True, help_text="URL to cover image (16:9 aspect ratio recommended)"
    )

    def __str__(self):
        return self.title


class Video(PublishableModel):
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(
        help_text="Full YouTube URL (e.g. https://youtube.com/watch?v=ID)",
        validators=[validate_youtube_url],
    )
    duration_minutes = models.PositiveSmallIntegerField(help_text="Duration in minutes")
    related_symptoms = models.ManyToManyField(Symptom, blank=True)

    def __str__(self):
        return self.title
