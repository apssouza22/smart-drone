import math
import threading
import time

import cv2
from djitellopy import tello as drone


class Drone:
	is_flying = False

	def __init__(self, mock: bool):
		self.sdk = drone.Tello()
		self.drone_locator = DroneLocator()
		self.drone_locator.watch()
		self.mock = mock
		self.video_stream = self.start_stream()

	def start(self):
		if self.mock:
			print("Starting mocked drone")
			return

		self.sdk.connect()
		self.sdk.streamon()

	def get_frame(self):
		return self.video_stream()

	def start_stream(self):
		if not self.mock:
			return lambda: self.sdk.get_frame_read().frame

		cap = cv2.VideoCapture(0)
		return lambda: cap.read()[1]

	def get_battery(self):
		self.sdk.get_battery()

	def takeoff(self):
		self.is_flying = True
		self.sdk.takeoff()

	def land(self):
		self.is_flying = False
		self.sdk.land()

	def update(self, right_left, forward_back, up_down, rotation):
		self.sdk.send_rc_control(right_left, forward_back, up_down, rotation)
		self.drone_locator.update_axis(right_left, forward_back, up_down, rotation)

	def get_position_history(self):
		return self.drone_locator.points

	def clean_position_history(self):
		self.drone_locator.points = [(0, 0)]


class DroneLocator:
	interval = 0.25  # interval to draw the map
	move_speed = 25 * interval
	rotation_speed = 72 * interval
	x, y = 350, 350
	accumulated_angle = 0
	points = [(0, 0), (0, 0)]
	distance = 0
	angle = 0
	axis_speed = {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}

	def watch(self):
		"""Watch for drone moves"""

		def draw_map(locator: DroneLocator, gambi):
			while True:
				locator.update()
				time.sleep(DroneLocator.interval)

		td = threading.Thread(target=draw_map, args=(self, ""))
		td.start()

	def update_axis(self, right_left, forward_back, up_down, rotation):
		self.axis_speed = {"rotation": rotation, "right-left": right_left, "forward-back": forward_back, "up-down": up_down}

	def update(self):
		self.calculate_current_position()
		if self.points[-1][0] != self.x or self.points[-1][1] != self.y:
			self.points.append((self.x, self.y))

	def calculate_current_position(self):
		distance = 0
		direction = 0

		# left
		if self.axis_speed["right-left"] < 0:
			distance = self.move_speed
			direction = -90

		# right
		if self.axis_speed["right-left"] > 0:
			distance = self.move_speed
			direction = 90

		# Forward
		if self.axis_speed["forward-back"] > 0:
			distance = self.move_speed
			direction = 0

		# Backward
		if self.axis_speed["forward-back"] < 0:
			distance = self.move_speed
			direction = 180

		# Rotation left
		if self.axis_speed["rotation"] < 0:
			self.accumulated_angle -= self.rotation_speed

		# Rotation right
		if self.axis_speed["rotation"] > 0:
			self.accumulated_angle += self.rotation_speed

		self.angle = direction + self.accumulated_angle

		self.x += int(distance * math.cos(math.radians(self.angle)))
		self.y += int(distance * math.sin(math.radians(self.angle)))

