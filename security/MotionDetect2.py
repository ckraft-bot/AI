from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

# Construct the argument parser and parse the command-line arguments
ap = argparse.ArgumentParser() 
ap.add_argument("-v", "--video", help="Path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="Minimum area size to detect motion")
args = vars(ap.parse_args())

# If no video file path is provided, use the webcam for video capture
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)  # Allow the camera sensor to warm up

# Otherwise, load the video file
else:
	vs = cv2.VideoCapture(args["video"])

# Initialize the first frame in the video stream (used to detect motion)
firstFrame = None

# Loop over the frames of the video stream
while True:
	# Grab the current frame
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"  # Default status text for the room
	
	# If the frame could not be grabbed, we've reached the end of the video
	if frame is None:
		break
	
	# Resize the frame, convert it to grayscale, and blur it to reduce noise
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)