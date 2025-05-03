from django.db import migrations, models
import education.validators


class Migration(migrations.Migration):

    dependencies = [
        ("education", "0004_alter_article_cover_image_alter_article_tags_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="video",
            old_name="youtube_url",
            new_name="video_url",
        ),
        migrations.AddField(
            model_name="video",
            name="youtube_url",
            field=models.URLField(
                blank=True, help_text="Legacy field - will be removed", null=True
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="cover_image",
            field=models.URLField(
                blank=True,
                help_text="URL to cover image (16:9 aspect ratio recommended)",
                validators=[education.validators.validate_image_url],
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="tags",
            field=models.JSONField(
                blank=True,
                default=education.models.Article.default_tags,
                help_text="List of tag strings, e.g., ['tag1', 'tag2']",
                validators=[education.validators.validate_string_list],
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="duration_minutes",
            field=models.PositiveSmallIntegerField(
                help_text="Duration in minutes (max 600 minutes / 10 hours)",
                validators=[education.validators.validate_duration_minutes],
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video (can be YouTube, Vimeo, or any other video platform)",
                null=True,
                validators=[education.validators.validate_video_url],
            ),
        ),
    ]
