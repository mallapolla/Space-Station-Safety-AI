from pathlib import Path

import cv2

from .utils import ensure_output_dir, run_inference


def run_image_detection(image_path: str) -> dict:
    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError("Uploaded image could not be read by OpenCV.")

    result = run_inference(frame)
    output_dir = ensure_output_dir("results", "images")
    output_path = output_dir / f"detected_{Path(image_path).stem}.jpg"
    cv2.imwrite(str(output_path), result["annotated_frame"])

    return {
        "output_path": str(output_path),
        "detected_objects": result["detected_objects"],
        "avg_confidence": result["avg_confidence"],
        "frame_count": result["frame_count"],
        "fps": result["fps"],
    }
