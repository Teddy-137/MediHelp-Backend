from django.contrib import admin
from .models import FirstAidInstruction, HomeRemedy


class FirstAidInstructionAdmin(admin.ModelAdmin):
    list_display = ("title", "condition", "severity_level_display", "created_at")
    list_filter = ("severity_level", "condition")
    search_fields = ("title", "description", "condition__name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "description", "condition", "severity_level")}),
        (
            "Steps",
            {
                "fields": ("steps",),
                "description": 'Enter steps as a JSON array of strings, e.g., ["Step 1", "Step 2"]',
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def severity_level_display(self, obj):
        return obj.get_severity_level_display()

    severity_level_display.short_description = "Severity"


class HomeRemedyAdmin(admin.ModelAdmin):
    list_display = ("name", "symptom_list", "created_at")
    list_filter = ("symptoms",)
    search_fields = ("name", "preparation", "symptoms__name")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("symptoms",)
    fieldsets = (
        (None, {"fields": ("name", "symptoms", "preparation")}),
        (
            "Ingredients",
            {
                "fields": ("ingredients",),
                "description": 'Enter ingredients as a JSON array of strings, e.g., ["Ingredient 1", "Ingredient 2"]',
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def symptom_list(self, obj):
        return ", ".join([s.name for s in obj.symptoms.all()[:3]]) + (
            "..." if obj.symptoms.count() > 3 else ""
        )

    symptom_list.short_description = "Symptoms"


admin.site.register(FirstAidInstruction, FirstAidInstructionAdmin)
admin.site.register(HomeRemedy, HomeRemedyAdmin)
