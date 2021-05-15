import threading
import time

import cv2
import numpy as np
import math


class PathMapper:
	""" Draw the drone path"""

	interval = 0.25  # interval to draw the map
	move_speed = 25 * interval  # 25cm per second
	rotation_speed = 72 * interval  # 72 degrees per second
	x, y = 400, 500
	angle = 0
	angle_sum = 0
	points = [(0, 0), (0, 0)]
	distance = 0
	display = True

	def calculate_current_position(self):
		self.angle += self.angle_sum
		self.x += int(self.distance * math.cos(math.radians(self.angle)))
		self.y += int(self.distance * math.sin(math.radians(self.angle)))

	def translate_drone_command(self, axis_speed: {}):
		"""Translate drone move into screen drawing"""
		# {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}
		self.display = True
		self.distance = 0
		self.angle = 0

		if axis_speed["right-left"] < 0:
			self.distance = self.move_speed
			self.angle = -90

		elif axis_speed["right-left"] > 0:
			self.distance = -self.move_speed
			self.angle = 90

		# Forward
		if axis_speed["forward-back"] > 0:
			self.distance = self.move_speed
			self.angle = 0

		# Backward
		elif axis_speed["forward-back"] < 0:
			self.distance = -self.move_speed
			self.angle = 180

		# Rotation left
		if axis_speed["rotation"] < 0:
			self.angle_sum -= self.rotation_speed

		# Rotation right
		elif axis_speed["rotation"] > 0:
			self.angle_sum += self.rotation_speed

	def draw_path(self, img=None):
		"""Draw drone moves"""
		if not self.display:
			return
		self.display = False

		self.calculate_current_position()

		if self.points[-1][0] != self.x or self.points[-1][1] != self.y:
			self.points.append((self.x, self.y))
		if img is None:
			img = np.zeros((1000, 800, 3), np.uint8)

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
		return img

	def watch(self, drone_controller):
		"""Watch for drone moves"""

		def draw_map(mapping, drone_control):
			while True:
				mapping.translate_drone_command(drone_control.axis_speed)
				time.sleep(PathMapper.interval)

		td = threading.Thread(target=draw_map, args=(self, drone_controller))
		td.start()
