import time

import cv2

from common.mapping import PathMapper
from pathplan.pathcontroller import PathController


class PathManager:

	def __init__(self, pygame_screen):
		self.pygame_screen = pygame_screen
		self.path_mapper = PathMapper()
		self.path_planning = PathController()
		self.path_planning_enabled = False

	def handle(self, axis_speed_source, is_flying):
		map_img, axis_speed = self.path_plan(is_flying)
		img = self.path_mapper.draw_path(map_img)

		if img is not None and not self.pygame_screen.plan_map_opened:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			self.pygame_screen.load_background(img)

		return axis_speed_source if axis_speed is None else axis_speed

	def path_plan(self, is_flying):
		map_img = None
		axis_speed = None

		if not is_flying or not self.path_planning_enabled:
			return map_img, axis_speed

		if not self.path_planning.contain_path_plan:
			self.path_planning.read_path_plan()
			self.path_mapper.points = [(0, 0)]
			time.sleep(1)
			return map_img, axis_speed

		if self.path_planning.done:
			self.path_planning_enabled = False
			return map_img, axis_speed

		self.handle_rotation()
		self.handle_point_reached()
		axis_speed = self.path_planning.get_command()
		map_img = self.path_planning.draw_way_points()

		return map_img, axis_speed

	def handle_point_reached(self):
		point_reached = self.path_planning.has_reached_point(self.path_mapper.x, self.path_mapper.y)
		if point_reached:
			self.path_mapper.x = self.path_planning.x
			self.path_mapper.y = self.path_planning.y
			self.path_planning.move()
			self.path_mapper.angle_rotation = self.path_planning.angle

	def handle_rotation(self):
		if self.path_planning.rotating:
			rotation_time = abs(self.path_planning.get_angle()) * 0.0133
			print("Drone rotation. Waiting " + str(rotation_time) + " ...")
			time.sleep(rotation_time)
			self.path_planning.rotating = False

	def watch(self, tello):
		self.path_mapper.watch(tello)
