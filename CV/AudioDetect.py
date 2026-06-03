"""
AudioDetect.py
Continuously listens for speech input and prints recognized text.
"""

import logging
import speech_recognition as sr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

AMBIENT_NOISE_DURATION = 0.2


def create_recognizer() -> sr.Recognizer:
    return sr.Recognizer()


def recognize_speech(recognizer: sr.Recognizer) -> str | None:
    """
    Captures a single utterance from the microphone and returns
    the lowercased transcription, or None if speech was unintelligible.
    """
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=AMBIENT_NOISE_DURATION)
        audio = recognizer.listen(mic)

    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        logger.debug("Speech was unintelligible; skipping.")
        return None
    except sr.RequestError as exc:
        logger.error("Speech recognition service unavailable: %s", exc)
        return None


def listen_loop() -> None:
    """Runs the speech recognition loop until interrupted."""
    recognizer = create_recognizer()
    logger.info("Listening… (press Ctrl+C to stop)")

    while True:
        try:
            text = recognize_speech(recognizer)
            if text:
                print(f"Recognized: {text}")
        except KeyboardInterrupt:
            logger.info("Stopped by user.")
            break


if __name__ == "__main__":
    listen_loop()