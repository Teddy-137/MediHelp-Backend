from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(GISModelAdmin):
    list_display = ("name", "address", "phone")
    search_fields = ("name", "address")
    list_filter = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "address", "phone")}),
        ("Location", {"fields": ("location",), "classes": ("wide",)}),
        (
            "Hours",
            {
                "fields": ("opening_hours",),
                "description": 'Enter opening hours as a JSON object, e.g., {"Monday": "9:00-17:00"}',
            },
        ),
    )
