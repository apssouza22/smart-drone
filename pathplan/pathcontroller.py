import math
import time

import cv2
import numpy as np

from common.utils import get_dist_btw_pos


class PathController:
	wp = [
		{
			"dist_cm": 100,
			"dist_px": 50,
			"angle_deg": 0,
			"angle_dir": "right"
		},
		{
			"dist_cm": 50,
			"dist_px": 25,
			"angle_deg": 90,
			"angle_dir": "right"
		}
		,
		{
			"dist_cm": 100,
			"dist_px": 50,
			"angle_deg": 90,
			"angle_dir": "left"
		}
	]
	current_point = -1
	forward_speed = 117 / 10  # Forward Speed in cm/s. It took 10s to move 117 centimeters  (15cm/s)
	angle_speed = 360 / 10  # Angular Speed Degrees per second. It took 10s to rotate 360 degrees  (50d/s)
	rotation_end_time = 0
	move_end_time = time.time()
	move_end_point = (0, 0)
	way_points = []
	x = 400
	y = 500
	angle = -90
	rotating = False
	drone_initial_angle = 0

	def has_next(self):
		return len(self.wp) >= self.current_point + 1

	def move(self):
		self.rotating = False
		if not self.has_next():
			return {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}

		self.current_point = self.current_point + 1

		self.angle +=self.get_angle()
		self.calculate_point()
		self.way_points.append((self.x, self.y))

	def get_command(self):
		if not self.has_next():
			return {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}

		if not self.rotating:
			return {"rotation": 0, "right-left": 0, "forward-back": 35, "up-down": 0}

		rotation_speed = 30
		if self.get_angle() > 0:
			rotation_speed = -30

		return {"rotation": rotation_speed, "right-left": 0, "forward-back": 0, "up-down": 0}

	def calculate_point(self):
		distance_px = self.wp[self.current_point]["dist_px"]
		self.x += int(distance_px * math.cos(math.radians(self.angle)))
		self.y += int(distance_px * math.sin(math.radians(self.angle)))

	def get_angle(self):
		angle = int(self.wp[self.current_point]["angle_deg"])
		if self.wp[self.current_point]["angle_dir"] == "left":
			angle = -angle
		return angle

	def get_next_angle(self):
		angle = int(self.wp[self.current_point + 1]["angle_deg"])
		if self.wp[self.current_point]["angle_dir"] == "left":
			angle = -angle
		return angle

	def draw_way_points(self, img=None):
		if img is None:
			img = np.zeros((1000, 800, 3), np.uint8)

		for point in self.way_points:
			cv2.circle(img, point, 8, (0, 255, 0), cv2.FILLED)
		return img

	def angle_direction(self):
		time_rotation = self.get_angle() / self.angle_speed
		self.rotation_end_time = time.time() + time_rotation
		return {"rotation": time_rotation, "right-left": 0, "forward-back": 0, "up-down": 0}

	def has_reached_point(self, x, y, angle):
		if self.current_point < 0:
			return True

		dist = get_dist_btw_pos((x, y), (self.x, self.y))
		if not self.has_next():
			return True

		if self.rotating:
			rotated = abs(self.drone_initial_angle) - abs(angle)
			print("Rotating...", rotated, self.get_next_angle())
			if self.get_next_angle() == abs(rotated):
				return True
			return False

		if dist < 5:
			self.rotating = True
			self.drone_initial_angle = angle

		return False
