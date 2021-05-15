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
	angle = 0
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
		self.current_point = self.current_point + 1

		self.angle += self.get_angle()
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

	def has_reached_point(self, x, y):
		if self.current_point < 0:
			return True

		dist = get_dist_btw_pos((x, y), (self.x, self.y))

		if dist < 5:
			self.rotating = True
			return True

		return False
