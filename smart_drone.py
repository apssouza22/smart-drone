import time

from tellogesturecontrol.utils import CvFpsCalc
from common.utils import *
import dlib

kp.init()
drone_conn = init_drone_connection()

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("resources/shape_predictor_68_face_landmarks.dat")
(jaw_x, jaw_y) = face_utils.FACIAL_LANDMARKS_IDXS["jaw"]

time.sleep(2.2)
w, h = 360, 240
pid = [0.4, 0.4, 0]
pError = 0
drone_speed = 35
drone_rotation_speed = 50

mapping = DroneMapping()
mapping.draw_path()

cv_fps_calc = CvFpsCalc(buffer_len=10)
while cap.isOpened():
	# fps = cv_fps_calc.get()
	if kp.is_key_pressed("q"): drone_conn.land(); time.sleep(3)
	if kp.is_key_pressed("e"): drone_conn.takeoff()

	_, img = cap.read()
	# img = drone_conn.get_frame_read().frame
	frame = cv2.resize(img, (w, h))

	frame, face_info = find_face_ml(frame, detector, predictor, [jaw_x, jaw_y])
	control, pError = get_drone_command(face_info, pid, w, pError, drone_speed, drone_rotation_speed)

	if control.has_command():
		mapping.translate_drone_command(control)
		time.sleep(mapping.interval)
		mapping.draw_path()

	drone_conn.send_rc_control(control.left_right, control.forward_back, control.up_down, control.rotation)
	cv2.imshow("Output", frame)

	# cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
# print("Center", info[0], "Area", info[1])
# if cv2.waitKey(1) & 0xFF == ord('q'):
# 	drone_conn.land()
# 	break
