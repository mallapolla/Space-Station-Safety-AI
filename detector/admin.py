from django.contrib import admin

from .models import DetectionResult, LiveSession, UploadedMedia


@admin.register(UploadedMedia)
class UploadedMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "media_type", "uploaded_at", "file")
    list_filter = ("media_type", "uploaded_at")


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_media", "avg_confidence", "created_at")
    search_fields = ("detected_objects",)


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "started_at", "ended_at")
    list_filter = ("status", "started_at")
