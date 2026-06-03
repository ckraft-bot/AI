"""
MotionDetection.py
Detects motion in a webcam feed or video file using frame differencing.

Usage:
    python MotionDetection.py                        # webcam
    python MotionDetection.py -v path/to/video.mp4  # video file
"""

import argparse
import logging
import time

import cv2
import imutils
from imutils.video import VideoStream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration -------------------------------------------------------

FRAME_WIDTH        = 500
BLUR_KERNEL        = (21, 21)
CAMERA_WARMUP_SECS = 2.0
CAMERA_INDEX       = 0
QUIT_KEY           = ord("q")

# -------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    ap = argparse.ArgumentParser(description="Motion detection via frame differencing.")
    ap.add_argument("-v", "--video", help="Path to a video file (omit to use webcam).")
    ap.add_argument(
        "-a", "--min-area",
        type=int,
        default=500,
        help="Minimum contour area (px²) to count as motion (default: 500).",
    )
    return ap.parse_args()


def open_source(video_path: str | None) -> VideoStream | cv2.VideoCapture:
    """Open the webcam or a video file and return the capture source."""
    if video_path is None:
        logger.info("No video file provided — using webcam (index %d).", CAMERA_INDEX)
        vs = VideoStream(src=CAMERA_INDEX).start()
        time.sleep(CAMERA_WARMUP_SECS)
        return vs

    logger.info("Opening video file: %s", video_path)
    return cv2.VideoCapture(video_path)


def read_frame(source, is_webcam: bool) -> cv2.Mat | None:
    """Read the next frame from *source*, normalising webcam vs file APIs."""
    frame = source.read()
    return frame if is_webcam else frame[1]


def preprocess(frame: cv2.Mat) -> tuple[cv2.Mat, cv2.Mat]:
    """
    Resize, greyscale, and blur a frame to prepare it for diffing.
    Returns (resized_color_frame, blurred_gray_frame) so the caller
    can use the color frame for annotation and the gray frame for
    diffing — both at the same dimensions.
    """
    resized = imutils.resize(frame, width=FRAME_WIDTH)
    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray    = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)
    return resized, gray


def run() -> None:
    """Main motion-detection loop."""
    args      = parse_args()
    is_webcam = args.video is None
    source    = open_source(args.video)

    first_frame: cv2.Mat | None = None
    logger.info("Starting motion detection. Press 'q' to quit.")

    try:
        while True:
            raw = read_frame(source, is_webcam)

            if raw is None:
                logger.info("End of video stream.")
                break

            frame, gray = preprocess(raw)

            # Initialise reference frame on first iteration
            if first_frame is None:
                first_frame = gray
                logger.debug("Reference frame captured.")
                continue

            # TODO: frame differencing, contour detection, annotation,
            #       and cv2.imshow / waitKey go here.

            if cv2.waitKey(1) & 0xFF == QUIT_KEY:
                logger.info("Quit key pressed. Exiting.")
                break
    finally:
        if is_webcam:
            source.stop()
        else:
            source.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()