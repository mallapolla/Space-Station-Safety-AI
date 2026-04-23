from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LiveSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("running", "Running"), ("stopped", "Stopped"), ("error", "Error")], default="running", max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="UploadedMedia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="uploads/%Y/%m/%d/")),
                ("media_type", models.CharField(choices=[("image", "Image"), ("video", "Video")], max_length=20)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="DetectionResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("result_file", models.FileField(upload_to="results/%Y/%m/%d/")),
                ("detected_objects", models.TextField(blank=True)),
                ("avg_confidence", models.FloatField(default=0.0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uploaded_media", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="results", to="detector.uploadedmedia")),
            ],
        ),
    ]
