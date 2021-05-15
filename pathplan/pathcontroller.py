import json
import math
import os
import time

import cv2
import numpy as np

from common.utils import get_dist_btw_pos


class PathController:
	wp = [
		{
			"dist_px": 80,
			"angle_deg": 0,
			"angle_dir": "right"
		},
		{
			"dist_px": 50,
			"angle_deg": 90,
			"angle_dir": "right"
		}
		,
		{
			"dist_px": 80,
			"angle_deg": 90,
			"angle_dir": "right"
		}
	]
	current_point = -1
	way_points = []
	x = 400
	y = 500
	angle = -90
	rotating = False
	drone_initial_angle = 0
	done = False
	rotation_direction = None
	adjust_rotation = 0

	def read_path_plan(self):
		if not os.path.exists("pathplan/waypoint.json"):
			return False
		f = open("pathplan/waypoint.json")
		self.wp = json.load(f)["wp"]
		return True

	def move(self):
		self.rotating = False
		self.current_point = self.current_point + 1

		self.angle += self.get_angle()
		self.angle += self.adjust_rotation
		self.calculate_point()
		self.way_points.append((self.x, self.y))

	def get_command(self):
		if self.done:
			return {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}
		if not self.rotating:
			return {"rotation": 0, "right-left": 0, "forward-back": 35, "up-down": 0}

		rotation_speed = 80
		if self.get_next_angle() < 0:
			rotation_speed = -80

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
		if len(self.wp) <= self.current_point + 1:
			return

		angle = int(self.wp[self.current_point + 1]["angle_deg"])
		if self.wp[self.current_point + 1]["angle_dir"] == "left":
			angle = -angle
		return angle

	def draw_way_points(self, img=None):
		if img is None:
			img = np.zeros((1000, 800, 3), np.uint8)

		for point in self.way_points:
			cv2.circle(img, point, 8, (0, 255, 0), cv2.FILLED)
		return img

	def has_reached_point(self, x, y, drone_angle):
		if self.current_point < 0:
			return True

		dist = get_dist_btw_pos((x, y), (self.x, self.y))

		if self.rotating:
			# time.sleep(0.20)
			return self.is_rotation_complete(drone_angle)

		if dist < 3:
			self.rotating = True
			self.drone_initial_angle = drone_angle
			if self.get_next_angle() is None:
				self.done = True
				return False
			self.rotation_direction = self.wp[self.current_point + 1]["angle_dir"]

		return False

	def is_rotation_complete(self, angle):
		rotated = abs(self.drone_initial_angle) - abs(angle)
		print("Rotating...", angle, self.angle)
		if abs(self.get_next_angle()) == abs(rotated):
			return True
		if self.rotation_direction == "right" and abs(self.get_next_angle()) < abs(rotated):
			self.adjust_rotation = abs(abs(self.get_next_angle()) - abs(rotated))
			return True
		if self.rotation_direction == "left" and abs(self.get_next_angle()) < abs(rotated):
			if self.adjust_rotation ==0:
				self.adjust_rotation = abs(self.get_next_angle()) - abs(rotated)
			return True
		return False
