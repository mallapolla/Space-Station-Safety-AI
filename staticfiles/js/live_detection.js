const startButton = document.getElementById("startLiveBtn");
const stopButton = document.getElementById("stopLiveBtn");
const videoElement = document.getElementById("liveVideo");
const canvasElement = document.getElementById("captureCanvas");
const outputImage = document.getElementById("annotatedFrame");
const fpsValue = document.getElementById("fpsValue");
const objectCount = document.getElementById("objectCount");
const avgConfidence = document.getElementById("avgConfidence");
const statusText = document.getElementById("liveStatus");
const detectedObjectsList = document.getElementById("detectedObjectsList");
const detectionCards = document.getElementById("detectionCards");
const trackingToggle = document.getElementById("trackingToggle");
const startMjpegButton = document.getElementById("startMjpegBtn");
const stopMjpegButton = document.getElementById("stopMjpegBtn");
const mjpegStream = document.getElementById("mjpegStream");
const topObject = document.getElementById("topObject");
const trackingStatus = document.getElementById("trackingStatus");
const liveStateValue = document.getElementById("liveStateValue");
const feedModeLabel = document.getElementById("feedModeLabel");

let mediaStream = null;
let captureInterval = null;
let isProcessing = false;

async function postJson(url, payload = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.liveDetectionConfig.csrfToken,
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || data.message || "Request failed.");
    }
    return data;
}

async function startLiveDetection() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        statusText.textContent = "Webcam API is not available in this browser. Use the MJPEG fallback below.";
        return;
    }

    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        videoElement.srcObject = mediaStream;
        await videoElement.play();

        await postJson(window.liveDetectionConfig.startUrl);
        stopMjpegStream();
        startButton.disabled = true;
        stopButton.disabled = false;
        liveStateValue.textContent = "ACTIVE";
        if (feedModeLabel) {
            feedModeLabel.textContent = "Browser Camera";
        }
        statusText.textContent = "Live detection started. Processing browser webcam frames...";

        captureInterval = window.setInterval(captureAndSendFrame, 280);
    } catch (error) {
        liveStateValue.textContent = "ERROR";
        statusText.textContent = `Unable to start webcam detection: ${error.message}`;
    }
}

async function captureAndSendFrame() {
    if (!mediaStream || isProcessing || videoElement.readyState < 2) {
        return;
    }

    isProcessing = true;

    const context = canvasElement.getContext("2d");
    canvasElement.width = videoElement.videoWidth || 640;
    canvasElement.height = videoElement.videoHeight || 480;
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

    try {
        const frame = canvasElement.toDataURL("image/jpeg", 0.8);
        const data = await postJson(window.liveDetectionConfig.frameUrl, {
            frame,
            track: trackingToggle.checked,
        });

        outputImage.src = data.annotated_frame;
        fpsValue.textContent = Number(data.fps || 0).toFixed(2);
        objectCount.textContent = data.frame_count || 0;
        avgConfidence.textContent = `${(Number(data.avg_confidence || 0) * 100).toFixed(1)}%`;
        trackingStatus.textContent = trackingToggle.checked ? "ON" : "OFF";
        liveStateValue.textContent = "SCANNING";
        statusText.textContent = "Detection is running.";
        renderDetectedObjects(data.detected_objects || []);
        renderDetectionCards(data.detections || []);
    } catch (error) {
        liveStateValue.textContent = "ERROR";
        statusText.textContent = `Frame processing error: ${error.message}`;
    } finally {
        isProcessing = false;
    }
}

function renderDetectedObjects(objects) {
    detectedObjectsList.innerHTML = "";
    if (!objects.length) {
        detectedObjectsList.innerHTML = '<span class="neon-badge">No objects detected</span>';
        return;
    }

    objects.forEach((label) => {
        const badge = document.createElement("span");
        badge.className = "neon-badge";
        badge.textContent = label;
        detectedObjectsList.appendChild(badge);
    });

    topObject.textContent = objects[0] ? objects[0].split("(")[0].trim().toUpperCase() : "NONE";
}

function renderDetectionCards(detections) {
    if (!detectionCards) {
        return;
    }

    detectionCards.innerHTML = "";
    if (!detections.length) {
        detectionCards.innerHTML = '<div class="detection-card empty">No active detections in this frame.</div>';
        return;
    }

    detections.slice(0, 6).forEach((item) => {
        const card = document.createElement("div");
        card.className = "detection-card";
        const confidence = `${(Number(item.confidence || 0) * 100).toFixed(1)}%`;
        const trackId = item.track_id !== undefined ? ` | Track ${item.track_id}` : "";
        card.innerHTML = `
            <strong>${item.class_name}</strong>
            <span>Confidence ${confidence}${trackId}</span>
        `;
        detectionCards.appendChild(card);
    });
}

async function stopLiveDetection() {
    if (captureInterval) {
        window.clearInterval(captureInterval);
        captureInterval = null;
    }

    if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
        mediaStream = null;
    }

    videoElement.srcObject = null;
    startButton.disabled = false;
    stopButton.disabled = true;
    liveStateValue.textContent = "IDLE";
    statusText.textContent = "Live detection stopped.";
    trackingStatus.textContent = "OFF";

    try {
        await postJson(window.liveDetectionConfig.stopUrl);
    } catch (error) {
        statusText.textContent = `Session stop warning: ${error.message}`;
    }
}

function startMjpegStream() {
    stopLiveDetection();
    mjpegStream.src = `${window.liveDetectionConfig.mjpegUrl}?_ts=${Date.now()}`;
    startMjpegButton.disabled = true;
    stopMjpegButton.disabled = false;
    liveStateValue.textContent = "MJPEG";
    if (feedModeLabel) {
        feedModeLabel.textContent = "MJPEG Standby";
    }
    statusText.textContent = "MJPEG fallback stream started.";
}

function stopMjpegStream() {
    if (!mjpegStream) {
        return;
    }
    mjpegStream.removeAttribute("src");
    startMjpegButton.disabled = false;
    stopMjpegButton.disabled = true;
    if (!mediaStream) {
        liveStateValue.textContent = "IDLE";
    }
}

if (startButton && stopButton) {
    startButton.addEventListener("click", startLiveDetection);
    stopButton.addEventListener("click", stopLiveDetection);
    window.addEventListener("beforeunload", stopLiveDetection);
}

if (startMjpegButton && stopMjpegButton) {
    startMjpegButton.addEventListener("click", startMjpegStream);
    stopMjpegButton.addEventListener("click", stopMjpegStream);
}

if (trackingToggle && trackingStatus) {
    trackingToggle.addEventListener("change", () => {
        trackingStatus.textContent = trackingToggle.checked ? "ON" : "OFF";
    });
}
