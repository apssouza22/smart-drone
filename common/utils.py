import math
from imutils import face_utils
import cv2
import numpy as np
from djitellopy import tello
from common import keypress as kp


class ControlCommand:
	left_right = 0
	forward_back = 0
	up_down = 0
	rotation = 0

	def has_command(self):
		if (
				self.left_right == 0 and
				self.forward_back == 0 and
				self.up_down == 0 and
				self.rotation == 0
		):
			return False
		return True


def handle_keyboard_input(drone_speed, drone_rotation_speed):
	cc = ControlCommand()
	if kp.is_key_pressed("LEFT"):
		cc.left_right = -drone_speed

	elif kp.is_key_pressed("RIGHT"):
		cc.left_right = drone_speed

	# Forward
	if kp.is_key_pressed("UP"):
		cc.forward_back = drone_speed

	# Backward
	elif kp.is_key_pressed("DOWN"):
		cc.forward_back = -drone_speed

	# UP
	if kp.is_key_pressed("w"):
		cc.up_down = drone_speed

	# Down
	elif kp.is_key_pressed("s"):
		cc.up_down = -drone_speed

	# Rotation left
	if kp.is_key_pressed("a"):
		cc.rotation = -drone_rotation_speed

	# Rotation right
	elif kp.is_key_pressed("d"):
		cc.rotation = drone_rotation_speed

	return cc


class DroneMapping:
	forward_speed = 117 / 10  # Forward Speed in cm/s. It took 10s to move 117 centimeters  (15cm/s)
	angularSpeed = 360 / 10  # Angular Speed Degrees per second. It took 10s to rotate 360 degrees  (50d/s)
	interval = 0.25  # interval to draw the map
	distance_interval = forward_speed * interval
	angle_interval = angularSpeed * interval
	x, y = 500, 500
	angle = 0
	angle_sum = 0
	points = [(0, 0), (0, 0)]
	distance = 0

	def calculate_current_position(self):
		self.angle += self.angle_sum
		self.x += int(self.distance * math.cos(math.radians(self.angle)))
		self.y += int(self.distance * math.sin(math.radians(self.angle)))

	def translate_drone_command(self, ctrl):
		self.distance = 0
		self.angle = 0

		if ctrl.left_right < 0:
			self.distance = self.distance_interval
			self.angle = -180

		elif ctrl.left_right > 0:
			self.distance = -self.distance_interval
			self.angle = 180

		# Forward
		if ctrl.forward_back > 0:
			self.distance = self.distance_interval
			self.angle = 270

		# Backward
		elif ctrl.forward_back < 0:
			self.distance = -self.distance_interval
			self.angle = -90

		# Rotation left
		if ctrl.rotation < 0:
			self.angle_sum -= self.angle_interval

		# Rotation right
		elif ctrl.rotation > 0:
			self.angle_sum += self.angle_interval

	def draw_path(self):
		self.calculate_current_position()
		if self.points[-1][0] != self.x or self.points[-1][1] != self.y:
			self.points.append((self.x, self.y))

		img = np.zeros((1000, 1000, 3), np.uint8)
		for point in self.points:
			cv2.circle(img, point, 5, (0, 0, 255), cv2.FILLED)

		cv2.circle(img, self.points[-1], 8, (0, 255, 0), cv2.FILLED)
		cv2.putText(
			img,
			f'({(self.points[-1][0] - 500) / 100},{(self.points[-1][1] - 500) / 100})m',
			(self.points[-1][0] + 10, self.points[-1][1] + 30), cv2.FONT_HERSHEY_PLAIN,
			1, (255, 0, 255), 1
		)
		cv2.imshow("Map", img)


def find_face(img):
	face_cascade = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(img_gray, 1.2, 8)
	faces_center_position = []
	faces_area = []

	for (x, y, w, h) in faces:
		center_x = x + w // 2
		center_y = y + h // 2
		face_area = w * h
		cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
		cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), cv2.FILLED)
		faces_center_position.append([center_x, center_y])
		faces_area.append(face_area)

	if len(faces_area) != 0:
		i = faces_area.index(max(faces_area))
		return img, [faces_center_position[i], faces_area[i]]
	else:
		return img, [[0, 0], 0]


def find_face_area(x, y, w, h):
	center_x = x + w // 2
	center_y = y + h // 2
	face_area = w * h
	return face_area, [center_x, center_y]


def find_face_ml(frame, detector, predictor, part_cordinate):
	gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces_center_position = []
	faces_area = []
	faces = detector(gray_img, 0)
	# loop over the face detections
	for rect in faces:
		shape = predictor(gray_img, rect)
		shape = face_utils.shape_to_np(shape)
		jaw_np = shape[part_cordinate[0]:part_cordinate[1]]

		(x, y, w, h) = cv2.boundingRect(np.array([jaw_np]))
		face_area, face_center = find_face_area(x, y, w, h)

		faces_center_position.append(face_center)
		faces_area.append(face_area)

		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
		cv2.circle(frame, (face_center[0], face_center[1]), 5, (0, 255, 0), cv2.FILLED)

	if len(faces_area) != 0:
		i = faces_area.index(max(faces_area))
		return frame, [faces_center_position[i], faces_area[i]]
	else:
		return frame, [[0, 0], 0]


def get_move_distance(area):
	distance_range = [6200, 6800]
	if area > distance_range[0] and area < distance_range[1]:
		return 0
	if area > distance_range[1]:
		return -20
	elif area < distance_range[0] and area != 0:
		return 20
	return 0


def calculate_pid_rotation(center_x, pError, pid, width):
	error = center_x - width // 2
	rotation = pid[0] * error + pid[1] * (error - pError)
	# rotation will be between -100 and 100
	rotation = int(np.clip(rotation, -100, 100))
	return error, rotation


def face_exists(info):
	if info[0][0] != 0:
		return True
	return False


cap = cv2.VideoCapture(0)


def get_drone_command(face_info, pid, w, error_adjust, drone_speed=15, drone_rotation_speed=50):
	center_x = face_info[0][0]
	control = ControlCommand()
	if face_exists(face_info):
		error_adjust, control.rotation = calculate_pid_rotation(center_x, error_adjust, pid, w)
		control.forward_back = get_move_distance(face_info[1])
	else:
		# time.sleep(0.25)
		control = handle_keyboard_input(
			drone_speed,
			drone_rotation_speed
		)

	return control, error_adjust


def init_drone_connection():
	drone = tello.Tello()
	drone.connect()
	print(drone.get_battery())
	drone.streamon()
	return drone
