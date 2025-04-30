from django.contrib import admin
from .models import Article, Video


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_date")
    search_fields = ("title", "summary", "content")
    list_filter = ("is_published", "published_date")
    ordering = ("-published_date",)


class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_date")
    search_fields = ("title",)
    list_filter = ("is_published", "published_date")
    ordering = ("-published_date",)


admin.site.register(Article, ArticleAdmin)
admin.site.register(Video, VideoAdmin)
