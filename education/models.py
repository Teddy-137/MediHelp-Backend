from django.db import models
from symptoms.models import Condition, Symptom
from .validators import (
    validate_string_list,
    validate_video_url,
    validate_image_url,
    validate_duration_minutes,
)


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

    def default_tags():
        return []

    tags = models.JSONField(
        blank=True,
        default=default_tags,
        help_text="List of tag strings, e.g., ['tag1', 'tag2']",
        validators=[validate_string_list],
    )
    cover_image = models.URLField(
        blank=True,
        help_text="URL to cover image (16:9 aspect ratio recommended)",
        validators=[validate_image_url],
    )

    def __str__(self):
        return self.title


class Video(PublishableModel):
    title = models.CharField(max_length=200)
    video_url = models.URLField(
        help_text="URL to the video (can be YouTube, Vimeo, or any other video platform)",
        validators=[validate_video_url],
        blank=True,
        null=True,
    )
    youtube_url = models.URLField(
        help_text="Legacy field - will be removed",
        blank=True,
        null=True,
    )
    duration_minutes = models.PositiveSmallIntegerField(
        help_text="Duration in minutes (max 600 minutes / 10 hours)",
        validators=[validate_duration_minutes],
    )
    related_symptoms = models.ManyToManyField(Symptom, blank=True)

    def __str__(self):
        return self.title
