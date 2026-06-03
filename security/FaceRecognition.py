"""
FaceRecognition.py

Current state: loads a reference image and previews its BGR vs RGB
color representation as a preprocessing step.

Planned pipeline:
    1. Face detection  - locating faces in the frame
    2. Face alignment  - normalize faces with the training database
    3. Feature extraction - focusing on details of the face
    4. Face recognition - matching faces against the database
"""

import logging
import sys
from pathlib import Path

import cv2
import face_recognition

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration -------------------------------------------------------

IMAGE_PATH = Path(r"<path>\BillGates.jpg")

# -------------------------------------------------------------------------


def load_image(path: Path) -> cv2.Mat:
    """Load an image via face_recognition; exit with a clear message if missing."""
    if not path.exists():
        logger.error("Image not found: %s", path)
        sys.exit(1)
    return face_recognition.load_image_file(str(path))


def display_bgr_and_rgb(image_bgr: cv2.Mat) -> None:
    """
    ######################### Face Recognition #########################
    Show both the raw BGR image returned by face_recognition and its
    correct RGB representation side-by-side so the color difference is
    immediately visible.
    """
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    cv2.imshow("BGR Image", image_bgr)
    cv2.imshow("RGB Image", image_rgb)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run() -> None:
    """Load the reference image and kick off the display pipeline."""
    logger.info("Loading image: %s", IMAGE_PATH)
    image = load_image(IMAGE_PATH)

    display_bgr_and_rgb(image)


if __name__ == "__main__":
    run()