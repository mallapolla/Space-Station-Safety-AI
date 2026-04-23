from django.urls import path

from . import views


app_name = "detector"

urlpatterns = [
    path("", views.home, name="home"),
    path("live/", views.live_detection_page, name="live_detection"),
    path("image/", views.image_detection_page, name="image_detection"),
    path("video/", views.video_detection_page, name="video_detection"),
    path("history/", views.history_page, name="history"),
    path("about/", views.about_page, name="about"),
    path("api/live/start/", views.start_live_session, name="start_live_session"),
    path("api/live/stop/", views.stop_live_session, name="stop_live_session"),
    path("api/live/frame/", views.live_frame_api, name="live_frame_api"),
    path("api/live/stream/", views.live_mjpeg_stream, name="live_mjpeg_stream"),
]
