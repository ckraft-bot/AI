import cv2
import numpy as np
import dlib

# Connect to the camera
cap = cv2.VideoCapture(0)

# Initialize the face detector
detector = dlib.get_frontal_face_detector()

# Start capturing video frames
while True:
 
    # Capture frame-by-frame from the camera
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Flip the frame horizontally
 
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
 
    # Initialize face counter
    i = 0
    
    # Loop through all detected faces
    for face in faces:
        # Get coordinates of the face
        x, y = face.left(), face.top()
        x1, y1 = face.right(), face.bottom()
        
        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
 
        # Increment face counter
        i += 1
 
        # Add face number label to the detected face
        cv2.putText(frame, 'Face ' + str(i), (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        print(face, i)
 
    # Display the frame with detected faces
    cv2.imshow('Frame', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
