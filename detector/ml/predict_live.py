import cv2

from .utils import decode_base64_image, encode_image_to_data_url, run_inference


def process_browser_frame(frame_data: str, enable_tracking: bool = False) -> dict:
    frame = decode_base64_image(frame_data)
    inference = run_inference(frame, enable_tracking=enable_tracking)
    encoded_frame = encode_image_to_data_url(inference["annotated_frame"])

    return {
        "annotated_frame": encoded_frame,
        "detections": inference["detections"],
        "detected_objects": inference["detected_objects"],
        "frame_count": inference["frame_count"],
        "avg_confidence": inference["avg_confidence"],
        "fps": inference["fps"],
    }


def generate_mjpeg_stream(enable_tracking: bool = False):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Webcam not available. Check camera permissions or device access.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            inference = run_inference(frame, enable_tracking=enable_tracking)
            ok, buffer = cv2.imencode(".jpg", inference["annotated_frame"])
            if not ok:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
    finally:
        camera.release()
