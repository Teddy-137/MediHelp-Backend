# Generated by Django 5.2 on 2025-04-29 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('symptoms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symptomcheck',
            name='ai_diagnosis',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
