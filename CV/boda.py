"""
boda.py  —  보다 ("to watch" in Korean)
Orchestrates audio detection, motion detection, and face counting
across background threads with a single annotated display window.

Usage:
    python boda.py                        # webcam
    python boda.py -v path/to/video.mp4  # video file
"""

import logging
import threading
import argparse
import sys
import time

import cv2
import dlib

from AudioDetect import recognize_speech, create_recognizer
from MotionDetection import preprocess
from FaceCount import detect_faces, annotate_frame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration -------------------------------------------------------

MOTION_THRESHOLD   = 500_000   # tune to your scene / lighting
CAMERA_INDEX       = 0
QUIT_KEY           = ord("q")
TRANSCRIPT_FADE    = 5.0       # seconds before transcription fades from overlay

OVERLAY = {
    "faces":  {"pos": (10, 30),  "color": (0, 255, 0)},
    "motion": {"pos": (10, 60),  "color": (0, 200, 255)},
    "audio":  {"pos": (10, 90),  "color": (0, 100, 255)},
}

# --- Shared state --------------------------------------------------------

_lock  = threading.Lock()
_state: dict = {
    "audio":      False,
    "motion":     False,
    "faces":      0,
    "transcript": "",        # last recognised utterance
    "transcript_ts": 0.0,   # timestamp of last update
}


def _update(key: str, value) -> None:
    with _lock:
        _state[key] = value


def _read() -> dict:
    with _lock:
        return _state.copy()

# --- Background workers --------------------------------------------------


def audio_worker() -> None:
    """Continuously listens on the microphone and updates audio + transcript state."""
    import speech_recognition as sr
    recognizer = create_recognizer()
    logger.info("Audio thread started.")

    while True:
        try:
            text = recognize_speech(recognizer)
            if text:
                with _lock:
                    _state["audio"]          = True
                    _state["transcript"]     = text
                    _state["transcript_ts"]  = time.monotonic()
                logger.info("Transcribed: %s", text)
            else:
                _update("audio", False)
        except Exception as exc:
            logger.debug("Audio worker error: %s", exc)
            _update("audio", False)

# --- Argument parsing ----------------------------------------------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="보다 — multi-sensor security monitor.")
    ap.add_argument("-v", "--video", help="Path to a video file (omit to use webcam).")
    return ap.parse_args()

# --- Helpers -------------------------------------------------------------


def open_camera(video_path: str | None) -> cv2.VideoCapture:
    src = video_path if video_path else CAMERA_INDEX
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        logger.error("Cannot open video source: %s", src)
        sys.exit(1)
    return cap


def get_screen_resolution() -> tuple[int, int]:
    """Return (width, height) of the primary display."""
    tmp = cv2.namedWindow("__probe__", cv2.WINDOW_NORMAL)
    cv2.moveWindow("__probe__", 0, 0)
    w = cv2.getWindowImageRect("__probe__")[2]
    h = cv2.getWindowImageRect("__probe__")[3]
    cv2.destroyWindow("__probe__")

    # Fallback: getWindowImageRect can return 0 before the window is shown
    if w <= 0 or h <= 0:
        import ctypes
        try:
            user32 = ctypes.windll.user32          # Windows
            w, h   = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        except AttributeError:
            w, h = 1920, 1080                       # safe default
    return w, h


def setup_window(name: str) -> None:
    """Create a resizable full-screen-fitted window."""
    screen_w, screen_h = get_screen_resolution()
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, screen_w, screen_h)
    cv2.moveWindow(name, 0, 0)


def draw_overlay(frame: cv2.Mat, state: dict) -> None:
    """Render live sensor readings and transcription onto the frame."""
    labels = {
        "faces":  f"Faces : {state['faces']}",
        "motion": f"Motion: {'YES' if state['motion'] else 'no'}",
        "audio":  f"Audio : {'YES' if state['audio'] else 'no'}",
    }
    for key, text in labels.items():
        cfg = OVERLAY[key]
        cv2.putText(frame, text, cfg["pos"],
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg["color"], 2)

    # Transcription overlay — shown until TRANSCRIPT_FADE seconds have elapsed
    transcript = state.get("transcript", "")
    age        = time.monotonic() - state.get("transcript_ts", 0.0)

    if transcript and age < TRANSCRIPT_FADE:
        h, w    = frame.shape[:2]
        label   = f'"{transcript}"'
        font    = cv2.FONT_HERSHEY_SIMPLEX
        scale   = 0.65
        thick   = 2

        (tw, th), baseline = cv2.getTextSize(label, font, scale, thick)

        # Centre horizontally, sit near the bottom of the frame
        tx = (w - tw) // 2
        ty = h - 30

        # Semi-transparent black backing for legibility
        cv2.rectangle(frame,
                      (tx - 6, ty - th - 6),
                      (tx + tw + 6, ty + baseline + 4),
                      (0, 0, 0), cv2.FILLED)

        cv2.putText(frame, label, (tx, ty), font, scale, (255, 255, 255), thick)


def detect_motion(gray: cv2.Mat, first_frame: cv2.Mat) -> bool:
    """Return True when frame difference exceeds the motion threshold."""
    diff   = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    return int(thresh.sum()) > MOTION_THRESHOLD

# --- Main loop -----------------------------------------------------------

WINDOW_NAME = "보다"


def run() -> None:
    args     = parse_args()
    cap      = open_camera(args.video)
    detector = dlib.get_frontal_face_detector()

    setup_window(WINDOW_NAME)
    threading.Thread(target=audio_worker, daemon=True).start()

    first_frame = None
    logger.info("boda is watching. Press 'q' to quit.")

    try:
        while True:
            ret, raw = cap.read()
            if not ret:
                logger.info("End of video stream.")
                break

            raw         = cv2.flip(raw, 1)
            frame, gray = preprocess(raw)

            # Initialise motion reference on first frame
            if first_frame is None:
                first_frame = gray
            else:
                _update("motion", detect_motion(gray, first_frame))

            # Face detection — reuses already-computed gray frame
            faces = detect_faces(detector, frame, gray)
            _update("faces", len(faces))
            annotate_frame(frame, faces)

            # Overlay + display
            draw_overlay(frame, _read())
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == QUIT_KEY:
                logger.info("Quit key pressed.")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("보다 stopped.")


if __name__ == "__main__":
    run()