import base64
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from django.conf import settings

ultralytics_dir = Path(settings.BASE_DIR) / ".ultralytics"
ultralytics_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(ultralytics_dir))

from ultralytics import YOLO


MODEL = None
LAST_FRAME_TIME = None
DEFAULT_CLASS_NAMES = [
    "Oxygen Tank",
    "Nitrogen Tank",
    "First Aid Box",
    "Fire Alarm",
    "Emergency Kit",
    "Helmet",
    "Safety Tool",
]


def load_model() -> YOLO:
    global MODEL
    if MODEL is None:
        model_path = Path(settings.YOLO_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model file not found at {model_path}. Place your custom best.pt there."
            )
        MODEL = YOLO(str(model_path))
    return MODEL


def ensure_output_dir(*parts: str) -> Path:
    directory = Path(settings.MEDIA_ROOT, *parts)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def decode_base64_image(data_url: str) -> np.ndarray:
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    decoded_bytes = base64.b64decode(data_url)
    np_array = np.frombuffer(decoded_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Unable to decode frame data from browser.")
    return frame


def encode_image_to_data_url(frame: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ok:
        raise ValueError("Unable to encode processed frame.")
    image_base64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{image_base64}"


def calculate_fps() -> float:
    global LAST_FRAME_TIME
    current_time = time.time()
    if LAST_FRAME_TIME is None:
        LAST_FRAME_TIME = current_time
        return 0.0
    elapsed = max(current_time - LAST_FRAME_TIME, 1e-6)
    LAST_FRAME_TIME = current_time
    return 1.0 / elapsed


def run_inference(frame: np.ndarray, enable_tracking: bool = False) -> dict[str, Any]:
    model = load_model()
    if enable_tracking:
        results = model.track(frame, persist=True, verbose=False)
    else:
        results = model(frame, verbose=False)

    result = results[0]
    annotated_frame = result.plot()
    boxes = result.boxes
    names_map = getattr(result, "names", {}) or getattr(model, "names", {})
    detections = []

    if boxes is not None:
        xyxy = boxes.xyxy.cpu().numpy() if boxes.xyxy is not None else []
        conf = boxes.conf.cpu().numpy() if boxes.conf is not None else []
        cls = boxes.cls.cpu().numpy() if boxes.cls is not None else []
        ids = boxes.id.cpu().numpy().astype(int).tolist() if getattr(boxes, "id", None) is not None else []

        for index, class_id in enumerate(cls):
            class_name = names_map.get(
                int(class_id),
                DEFAULT_CLASS_NAMES[int(class_id)] if int(class_id) < len(DEFAULT_CLASS_NAMES) else f"class_{int(class_id)}",
            )
            item = {
                "class_name": class_name,
                "confidence": round(float(conf[index]), 4) if len(conf) > index else 0.0,
                "box": [round(float(value), 2) for value in xyxy[index]] if len(xyxy) > index else [],
            }
            if ids and len(ids) > index:
                item["track_id"] = ids[index]
            detections.append(item)

    summary = summarize_detections(detections)
    overlay_metrics(annotated_frame, summary["frame_count"], summary["avg_confidence"], summary["fps"])

    return {
        "annotated_frame": annotated_frame,
        "detections": detections,
        "detected_objects": summary["detected_objects"],
        "frame_count": summary["frame_count"],
        "avg_confidence": summary["avg_confidence"],
        "fps": summary["fps"],
    }


def summarize_detections(detections: list[dict[str, Any]]) -> dict[str, Any]:
    object_names = [item["class_name"] for item in detections]
    frame_count = len(detections)
    avg_confidence = round(
        sum(item["confidence"] for item in detections) / frame_count, 4
    ) if frame_count else 0.0
    object_counter = Counter(object_names)
    detected_objects = [f"{name} ({count})" for name, count in object_counter.items()]
    return {
        "detected_objects": detected_objects,
        "frame_count": frame_count,
        "avg_confidence": avg_confidence,
        "fps": round(calculate_fps(), 2),
    }


def overlay_metrics(frame: np.ndarray, count: int, avg_confidence: float, fps: float) -> None:
    cv2.rectangle(frame, (10, 10), (320, 95), (7, 25, 55), -1)
    cv2.putText(frame, f"Objects: {count}", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Avg Conf: {avg_confidence:.2f}", (20, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 150), 2)
    cv2.putText(frame, f"FPS: {fps:.2f}", (20, 86), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
