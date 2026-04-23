# Real-Time Space Station Safety Object Detection System

This project is a beginner-friendly Django application for real-time safety object detection using Ultralytics YOLO, OpenCV, JavaScript, SQLite, HTML, and CSS.

## Main Features

- Live webcam detection from the browser using JavaScript frame capture and Django API inference
- OpenCV MJPEG streaming fallback for a simpler live demo
- Image upload detection with annotated image output
- Video upload detection with processed downloadable result video
- Detection history stored in SQLite
- Futuristic dashboard UI with FPS, object count, and confidence metrics
- Optional tracking support using `model.track()`

## Project Structure

```text
AI22/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── datasets/
│   └── space_station_safety/        # Put retraining dataset here
├── detector/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── ml/
│       ├── predict_image.py
│       ├── predict_live.py
│       ├── predict_video.py
│       └── utils.py
├── media/
│   ├── uploads/
│   └── results/
├── models/
│   └── best.pt                      # Put your custom YOLO model here
├── spacestation_safety/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── live_detection.js
└── templates/
    ├── base.html
    └── detector/
        ├── about.html
        ├── history.html
        ├── home.html
        ├── image_detection.html
        ├── live_detection.html
        └── video_detection.html
```

## Where To Put Important Files

### YOLO model file

Place your trained model file here:

```text
AI22/models/best.pt
```

### Dataset for retraining

Place your dataset here:

```text
AI22/datasets/space_station_safety/
```

Suggested dataset structure:

```text
space_station_safety/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

## Installation Steps

### 1. Create virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Put your custom model in the models folder

```text
AI22/models/best.pt
```

### 4. Run migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Django server

```powershell
python manage.py runserver
```

Open this in your browser:

```text
http://127.0.0.1:8000/
```

## How Live Detection Works

### Option 1: Browser webcam frame API method

1. The browser asks for webcam permission using `navigator.mediaDevices.getUserMedia()`.
2. JavaScript captures frames from the video stream.
3. Each frame is converted to base64 and sent to Django using `fetch()`.
4. Django decodes the frame, runs YOLO, draws boxes and labels, and returns the annotated frame.
5. JavaScript replaces the preview image continuously for live detection.

This method feels more like a real web application.

### Option 2: OpenCV plus Django MJPEG streaming method

1. Django opens the webcam using `cv2.VideoCapture(0)`.
2. Each frame is processed on the backend.
3. Django streams JPEG frames through a `StreamingHttpResponse`.
4. The frontend displays the stream inside an `<img>` tag.

This method is easier and more stable for many student projects because it uses less frontend logic.

## Which option is easier and more stable?

For a student project:

- Easier to explain: OpenCV plus Django MJPEG streaming
- Better web experience: Browser webcam frame API method
- Most stable on the same laptop running Django: OpenCV plus Django MJPEG streaming

## Database Tables

### UploadedMedia

- `id`
- `file`
- `media_type`
- `uploaded_at`

### DetectionResult

- `id`
- `uploaded_media`
- `result_file`
- `detected_objects`
- `avg_confidence`
- `created_at`

### LiveSession

- `id`
- `started_at`
- `ended_at`
- `status`

## Important Files Explained

- `detector/models.py`: database models for uploaded files, saved results, and live sessions
- `detector/forms.py`: upload forms for image and video pages
- `detector/views.py`: page rendering and API endpoints
- `detector/ml/utils.py`: common YOLO loading, frame encoding, inference, and FPS utilities
- `detector/ml/predict_image.py`: image inference logic
- `detector/ml/predict_video.py`: video inference logic
- `detector/ml/predict_live.py`: browser live-frame and MJPEG stream logic
- `static/js/live_detection.js`: live webcam logic on the frontend
- `static/css/style.css`: futuristic dashboard styling

## Commands Summary

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Future Enhancements

- RTSP/IP camera support
- Sound or email alerts for missing safety objects
- Advanced multi-object tracking with ByteTrack
- Detection analytics dashboard
- Role-based user login system
- Export results as CSV or PDF
- Live stream recording
