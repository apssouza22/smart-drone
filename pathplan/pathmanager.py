import time

import cv2

from common.drone import Drone
from common.mapping import PathMapper
from pathplan.pathcontroller import PathController


class PathManager:

	def __init__(self, pygame_screen, drone: Drone):
		self.drone = drone
		self.pygame_screen = pygame_screen
		self.path_mapper = PathMapper(drone)
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
		# is_flying = True
		# self.path_planning_enabled= True
		if not is_flying or not self.path_planning_enabled:
			return map_img, axis_speed

		if not self.path_planning.contain_path_plan:
			self.path_planning.read_path_plan()
			self.drone.clean_position_history()
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
		point_reached = self.path_planning.has_reached_point(self.drone.drone_locator.x, self.drone.drone_locator.y)
		if point_reached:
			self.drone.drone_locator.x = self.path_planning.x
			self.drone.drone_locator.y = self.path_planning.y
			self.path_planning.move()
			self.drone.drone_locator.accumulated_angle = self.path_planning.accumulated_angle
			self.drone.drone_locator.angle_calc_disabled = True

		if self.path_planning.done:
			self.drone.drone_locator.angle_calc_disabled = False

	def handle_rotation(self):
		if self.path_planning.rotating:
			rotation_time = abs(self.path_planning.angle) * 0.0133
			print("Drone rotation. Waiting " + str(rotation_time) + " ...")
			time.sleep(rotation_time)
			self.path_planning.rotating = False
