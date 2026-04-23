from django.db import models


class UploadedMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.media_type.title()} #{self.pk}"


class DetectionResult(models.Model):
    uploaded_media = models.ForeignKey(
        UploadedMedia,
        on_delete=models.CASCADE,
        related_name="results",
        null=True,
        blank=True,
    )
    result_file = models.FileField(upload_to="results/%Y/%m/%d/")
    detected_objects = models.TextField(blank=True)
    avg_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"DetectionResult #{self.pk}"


class LiveSession(models.Model):
    STATUS_CHOICES = (
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("error", "Error"),
    )

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")

    def __str__(self) -> str:
        return f"LiveSession #{self.pk} ({self.status})"
