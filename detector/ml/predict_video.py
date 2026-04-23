from pathlib import Path

import cv2

from .utils import ensure_output_dir, run_inference


def run_video_detection(video_path: str) -> dict:
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Uploaded video could not be opened.")

    fps = capture.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

    output_dir = ensure_output_dir("results", "videos")
    output_path = output_dir / f"detected_{Path(video_path).stem}.mp4"
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    all_confidences = []
    detected_names = set()
    total_frames = 0

    while True:
        success, frame = capture.read()
        if not success:
            break

        inference = run_inference(frame)
        writer.write(inference["annotated_frame"])
        total_frames += 1

        for item in inference["detections"]:
            all_confidences.append(item["confidence"])
            detected_names.add(item["class_name"])

    capture.release()
    writer.release()

    avg_confidence = round(sum(all_confidences) / len(all_confidences), 4) if all_confidences else 0.0
    return {
        "output_path": str(output_path),
        "detected_objects": sorted(detected_names),
        "avg_confidence": avg_confidence,
        "frame_count": total_frames,
        "fps": round(fps, 2),
    }
