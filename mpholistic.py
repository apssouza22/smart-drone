import cv2
import mediapipe as mp

from tellogesturecontrol.utils import CvFpsCalc

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(0)
holistic = mp_holistic.Holistic(
	min_detection_confidence=0.5,
	min_tracking_confidence=0.5
)
cv_fps_calc = CvFpsCalc(buffer_len=10)
while cap.isOpened():
	print(cv_fps_calc.get())

	success, image = cap.read()

	# Flip the image horizontally for a later selfie-view display, and convert
	# the BGR image to RGB.
	image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
	# To improve performance, optionally mark the image as not writeable to
	# pass by reference.
	image.flags.writeable = False
	results = holistic.process(image)

	# Draw landmark annotation on the image.
	image.flags.writeable = True
	image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
	mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
	mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
	mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
	mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
	cv2.imshow('MediaPipe Holistic', image)
	if cv2.waitKey(5) & 0xFF == 27:
		break
cap.release()
