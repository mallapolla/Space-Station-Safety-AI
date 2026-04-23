import json
from pathlib import Path

from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ImageUploadForm, VideoUploadForm
from .ml.predict_image import run_image_detection
from .ml.predict_live import generate_mjpeg_stream, process_browser_frame
from .ml.predict_video import run_video_detection
from .models import DetectionResult, LiveSession, UploadedMedia


def home(request):
    recent_results = DetectionResult.objects.select_related("uploaded_media").order_by("-created_at")[:5]
    supported_objects = [
        "Oxygen Tank",
        "Nitrogen Tank",
        "First Aid Box",
        "Fire Alarm",
        "Emergency Kit",
        "Helmet",
        "Safety Tool",
    ]
    stats = {
        "total_uploads": UploadedMedia.objects.count(),
        "total_results": DetectionResult.objects.count(),
        "live_sessions": LiveSession.objects.count(),
        "model_ready": Path(settings.YOLO_MODEL_PATH).exists(),
    }
    return render(
        request,
        "detector/home.html",
        {
            "recent_results": recent_results,
            "stats": stats,
            "supported_objects": supported_objects,
            "model_path": settings.YOLO_MODEL_PATH,
        },
    )


def live_detection_page(request):
    live_session = LiveSession.objects.filter(status="running").order_by("-started_at").first()
    return render(
        request,
        "detector/live_detection.html",
        {
            "live_session": live_session,
            "model_path": settings.YOLO_MODEL_PATH,
            "model_ready": Path(settings.YOLO_MODEL_PATH).exists(),
        },
    )


def image_detection_page(request):
    form = ImageUploadForm(request.POST or None, request.FILES or None)
    context = {"form": form}

    if request.method == "POST" and form.is_valid():
        uploaded_media = UploadedMedia.objects.create(
            file=form.cleaned_data["image"],
            media_type="image",
        )
        try:
            result = run_image_detection(uploaded_media.file.path)
            relative_result_path = _relative_media_path(result["output_path"])
            detection_result = DetectionResult.objects.create(
                uploaded_media=uploaded_media,
                result_file=relative_result_path,
                detected_objects=", ".join(result["detected_objects"]),
                avg_confidence=result["avg_confidence"],
            )
            context.update({"detection_result": detection_result, "image_stats": result})
            messages.success(request, "Image detection completed successfully.")
        except Exception as exc:
            messages.error(request, f"Image detection failed: {exc}")
            uploaded_media.delete()
    return render(request, "detector/image_detection.html", context)


def video_detection_page(request):
    form = VideoUploadForm(request.POST or None, request.FILES or None)
    context = {"form": form}

    if request.method == "POST" and form.is_valid():
        uploaded_media = UploadedMedia.objects.create(
            file=form.cleaned_data["video"],
            media_type="video",
        )
        try:
            result = run_video_detection(uploaded_media.file.path)
            relative_result_path = _relative_media_path(result["output_path"])
            detection_result = DetectionResult.objects.create(
                uploaded_media=uploaded_media,
                result_file=relative_result_path,
                detected_objects=", ".join(result["detected_objects"]),
                avg_confidence=result["avg_confidence"],
            )
            context.update({"detection_result": detection_result, "video_stats": result})
            messages.success(request, "Video detection completed successfully.")
        except Exception as exc:
            messages.error(request, f"Video detection failed: {exc}")
            uploaded_media.delete()
    return render(request, "detector/video_detection.html", context)


@require_GET
def history_page(request):
    results = DetectionResult.objects.select_related("uploaded_media").order_by("-created_at")
    return render(request, "detector/history.html", {"results": results})


def about_page(request):
    return render(request, "detector/about.html")


@require_POST
def start_live_session(request):
    LiveSession.objects.filter(status="running").update(status="stopped", ended_at=timezone.now())
    session = LiveSession.objects.create(status="running")
    return JsonResponse(
        {
            "message": "Live detection session started.",
            "session_id": session.id,
            "started_at": session.started_at.isoformat(),
        }
    )


@require_POST
def stop_live_session(request):
    session = LiveSession.objects.filter(status="running").order_by("-started_at").first()
    if session:
        session.status = "stopped"
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at"])
    return JsonResponse({"message": "Live detection session stopped."})


@csrf_exempt
@require_http_methods(["POST"])
def live_frame_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        frame_data = payload.get("frame", "")
        enable_tracking = bool(payload.get("track", False))
        result = process_browser_frame(frame_data, enable_tracking=enable_tracking)
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_GET
def live_mjpeg_stream(request):
    track_enabled = request.GET.get("track") == "1"
    stream = generate_mjpeg_stream(enable_tracking=track_enabled)
    return StreamingHttpResponse(
        stream,
        content_type="multipart/x-mixed-replace; boundary=frame",
    )


def _relative_media_path(absolute_path: str) -> str:
    from django.conf import settings

    return str(Path(absolute_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve()))
