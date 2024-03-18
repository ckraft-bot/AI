import cv2
import numpy as np
import dlib

#say cheeese, connecting to a camera
cap = cv2.VideoCapture(0)
#get the coordinates
detector = dlib.get_frontal_face_detector()

#count the num of faces
while True:
 
    #capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
 
    #operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
 
    #counter to count number of faces
    i = 0
    for face in faces:
        x, y = face.left(), face.top()
        x1, y1 = face.right(), face.bottom()
        cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
 
        #increment the iterartor each time you get the coordinates
        i = i+1
 
        # Adding face number to the box detecting faces
        cv2.putText(frame, 'face num'+str(i), (x-10, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        print(face, i)
 
    #Display the resulting frame
    cv2.imshow('frame', frame)

    #ok while this is fun the loop can't go on forever
    if cv2.waitKey(1) & 0xFF == ord('q'): #just type "Q" on the keyboard
        break

cap.release()
cv2.destroyAllWindows()

