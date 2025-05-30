# Generated by Django 5.2 on 2025-04-29 08:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('severity', models.PositiveSmallIntegerField(choices=[(1, 'Mild'), (2, 'Moderate'), (3, 'Severe')], default=1)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SymptomCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ai_diagnosis', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conditions', models.ManyToManyField(blank=True, to='symptoms.condition')),
                ('symptoms', models.ManyToManyField(to='symptoms.symptom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SymptomCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveSmallIntegerField(default=5)),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='symptoms.condition')),
                ('symptom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='symptoms.symptom')),
            ],
            options={
                'unique_together': {('symptom', 'condition')},
            },
        ),
        migrations.AddField(
            model_name='condition',
            name='symptoms',
            field=models.ManyToManyField(through='symptoms.SymptomCondition', to='symptoms.symptom'),
        ),
    ]
