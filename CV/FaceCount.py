"""
FaceCount.py
Real-time face detection via webcam using dlib's frontal face detector.
Press 'q' to quit.
"""

import logging
import sys

import cv2
import dlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration -------------------------------------------------------

CAMERA_INDEX    = 0
RECT_COLOR      = (0, 255, 0)   # Green bounding box
LABEL_COLOR     = (0, 0, 255)   # Red label text
FONT            = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE      = 0.7
FONT_THICKNESS  = 2
LABEL_OFFSET    = 10
QUIT_KEY        = ord("q")

# -------------------------------------------------------------------------


def open_camera(index: int = CAMERA_INDEX) -> cv2.VideoCapture:
    """Open the webcam; exit if unavailable."""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        logger.error("Cannot open camera at index %d.", index)
        sys.exit(1)
    return cap


def detect_faces(
    detector: dlib.fhog_object_detector,
    frame: cv2.Mat,
    gray: cv2.Mat | None = None,
) -> list:
    """
    Return dlib rectangles for every face found in *frame*.

    If a pre-computed grayscale version of the frame is provided via *gray*,
    it is used directly — skipping the conversion. This avoids redundant work
    when the caller (e.g. boda.py) has already produced a gray frame via
    preprocess().
    """
    if gray is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return detector(gray)


def annotate_frame(frame: cv2.Mat, faces: list) -> None:
    """Draw bounding boxes and labels on *frame* in-place."""
    for i, face in enumerate(faces, start=1):
        x, y, x1, y1 = face.left(), face.top(), face.right(), face.bottom()

        cv2.rectangle(frame, (x, y), (x1, y1), RECT_COLOR, 2)
        cv2.putText(
            frame,
            f"Face {i}",
            (x - LABEL_OFFSET, y - LABEL_OFFSET),
            FONT,
            FONT_SCALE,
            LABEL_COLOR,
            FONT_THICKNESS,
        )


def run() -> None:
    """Main capture-detect-display loop."""
    detector = dlib.get_frontal_face_detector()
    cap = open_camera()
    logger.info("Starting face detection. Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame; retrying…")
                continue

            frame = cv2.flip(frame, 1)
            faces = detect_faces(detector, frame)
            annotate_frame(frame, faces)

            if len(faces):
                logger.debug("Faces detected: %d", len(faces))

            cv2.imshow("Face Count", frame)

            if cv2.waitKey(1) & 0xFF == QUIT_KEY:
                logger.info("Quit key pressed. Exiting.")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()