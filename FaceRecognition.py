######################### Face Recognition #########################
""" 
Context: this purpose of this program will be to recognize faces. The outline will look like as follows:
    1. Face detection- locating faces in the frame
    2. Face alignment- normalize faces with the trianing database
    3. Feature extraction- focusing on details of the face that will help with training and recognition tasks
    4. Face recognition- matching faces against the datasets in the database
Extra downloads:
    - install Visual Studio for C++ for dlib
Libraries needed:
    - pip install dlib
        Dlib is a modern C++ toolkit containing machine learning algorithms and tools for creating complex software in C++ to solve real world problems. 
        It is used in both industry and academia in a wide range of domains including robotics, embedded devices, mobile phones, and large high performance computing environments. 
        Dlib's open source licensing allows you to use it in any application, free of charge. (source: http://dlib.net/)
    - pip install cmake
        CMake is used to control the software compilation process using simple platform and compiler independent configuration files, 
        and generate native makefiles and workspaces that can be used in the compiler environment of your choice. (source: https://pypi.org/project/cmake/)
    - pip3 install face_recognition OR pip install face_recognition
        Adam Geitgey created the face recogntion and made it open sourced. 
        This library is used to recognize and manipulate faces from Python or from the command line. (source: https://www.adamgeitgey.com/)
    - pip install opencv
        For image pre processing. 
"""

import cv2
import numpy as np
from scipy.misc import face
import face_recognition

## Load images
Gates_img_bgr = face_recognition.load_image_file(r"C:\Users\ckraft\Desktop\My Experiments\Personal Use\Images\BillGates.jpg")
Gates_img_rgb = cv2.cvtColor(Gates_img_bgr, cv2.COLOR_BGR2RGB)
cv2.imshow('bgr', Gates_img_bgr)
cv2.imshow('rgb', Gates_img_rgb)
cv2.waitKey(0)

## Locate face and draw a box

Gates_img = face_recognition.load_image_file(r"C:\Users\ckraft\Desktop\My Experiments\Personal Use\Images\BillGates.jpg")
