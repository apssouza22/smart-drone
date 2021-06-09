import cv2
import numpy as np

from common.drone import Drone


class PathMapper:
	""" Draw the drone path"""

	points = []

	def __init__(self, drone: Drone):
		self.drone = drone

	def draw_path(self, img=None):
		"""Draw drone moves"""
		points = self.drone.get_position_history()

		if len(points) == len(self.points):
			return

		self.points = points.copy()
		if img is None:
			img = np.zeros((1000, 800, 3), np.uint8)

		for point in points:
			cv2.circle(img, point, 5, (0, 0, 255), cv2.FILLED)

		cv2.circle(img, points[-1], 8, (0, 255, 0), cv2.FILLED)
		cv2.putText(
			img,
			f'({(points[-1][0] - 500) / 100},{(points[-1][1] - 500) / 100})m',
			(points[-1][0] + 10, points[-1][1] + 30), cv2.FONT_HERSHEY_PLAIN,
			1, (255, 0, 255), 1
		)
		return img
