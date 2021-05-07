import math
import time


class PathController:
	wp = [
		{
			"dist_cm": 155,
			"angle_deg": 90,
			"angle_dir": "right"
		},
		{
			"dist_cm": 50,
			"angle_deg": 90,
			"angle_dir": "right"
		}
		,
		{
			"dist_cm": 155,
			"angle_deg": 102,
			"angle_dir": "right"
		}
	]
	current_point = -1
	forward_speed = 117 / 10  # Forward Speed in cm/s. It took 10s to move 117 centimeters  (15cm/s)
	angle_speed = 360 / 10  # Angular Speed Degrees per second. It took 10s to rotate 360 degrees  (50d/s)
	rotation_end_time = 0
	move_end_time = time.time()

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
			self.distance = self.distance_interval
			self.angle = -180

		elif axis_speed["right-left"] > 0:
			self.distance = -self.distance_interval
			self.angle = 180

		# Forward
		if axis_speed["forward-back"] > 0:
			self.distance = self.distance_interval
			self.angle = 270

		# Backward
		elif axis_speed["forward-back"] < 0:
			self.distance = -self.distance_interval
			self.angle = -90

		# Rotation left
		if axis_speed["rotation"] < 0:
			self.angle_sum -= self.angle_interval

		# Rotation right
		elif axis_speed["rotation"] > 0:
			self.angle_sum += self.angle_interval

	def draw_path(self,):
		"""Draw drone moves"""
		if not self.display:
			return
		self.display = False

		self.calculate_current_position()

		if self.points[-1][0] != self.x or self.points[-1][1] != self.y:
			self.points.append((self.x, self.y))

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


	def next_point(self):
		self.current_point = self.current_point + 1
		if len(self.wp) <= self.current_point:
			print("End point")
			return {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}
		print("Next point")
		time_distance = self.wp[self.current_point]["dist_cm"] / self.forward_speed
		self.move_end_time = time.time() + time_distance
		return {"rotation": 0, "right-left": 0, "forward-back": 35, "up-down": 0}

	def angle_direction(self):
		time_rotation = self.wp[self.current_point]["angle_deg"] / self.angle_speed
		self.rotation_end_time = time.time() + time_rotation
		rotation_speed = int(self.wp[self.current_point]["angle_deg"])
		if self.wp[self.current_point]["angle_dir"] == "left":
			rotation_speed = -rotation_speed
		return {"rotation": rotation_speed, "right-left": 0, "forward-back": 0, "up-down": 0}

	def has_reached_point(self):
		print(self.move_end_time,time.time() )
		return self.move_end_time - time.time() < 0
