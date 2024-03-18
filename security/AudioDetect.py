import speech_recognition
import pyttsx3

#building the recognizer
recognizer = speech_recognition.Recognizer()

while True:
    try: 
        with speech_recognition.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration = 0.2)
            audio = recognizer.listen(mic)
            text = recognizer.recognize_google(audio)
            text = text.lower()

            print(f"Recognized {text}") #{As of Python 3.6, f-strings are a great new way to format strings. Not only are they more readable, more concise, and less prone to error than other ways of formatting, but they are also faster!}
    except speech_recognition.UnknownValueError():
        recognizer = speech_recognition.Recognizer()
        continue