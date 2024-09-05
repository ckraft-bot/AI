import speech_recognition
import pyttsx3

# Initialize the speech recognizer
recognizer = speech_recognition.Recognizer()

# Infinite loop to keep the program running and listening for speech input
while True:
    try: 
        # Use the microphone as the audio source
        with speech_recognition.Microphone() as mic:
            # Adjust for ambient noise to improve accuracy
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            
            # Listen for speech input from the microphone
            audio = recognizer.listen(mic)
            
            # Convert the speech to text using Google's speech recognition
            text = recognizer.recognize_google(audio)
            
            # Convert the recognized text to lowercase for uniformity
            text = text.lower()

            # Print the recognized text
            print(f"Recognized: {text}")
    
    # Handle exceptions when speech is not recognized
    except speech_recognition.UnknownValueError:
        # Reinitialize the recognizer in case of an unknown value error
        recognizer = speech_recognition.Recognizer()
        # Continue listening for more input
        continue
