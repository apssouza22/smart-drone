"""
Path tracking simulation with pure pursuit steering and PID speed control.
author: Atsushi Sakai (@Atsushi_twi)
        Guillaume Jacquenot (@Gjacquenot)
"""
import numpy as np
import math
import matplotlib.pyplot as plt

# Parameters
look_foward_gain = 0.1  # look forward gain
look_ahead_distance = 2.0  # [m] look-ahead distance
proportional_speed = 1.0  # speed proportional gain
interval = 0.1  # [s] time tick
angle_base = 2.9  # [m] wheel base of vehicle

show_animation = True


class Robot:

	def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
		self.x = x
		self.y = y
		self.yaw = yaw
		self.velocity = v
		self.x_and_yaw = self.x - ((angle_base / 2) * math.cos(self.yaw))
		self.y_and_yaw = self.y - ((angle_base / 2) * math.sin(self.yaw))

	def update(self, speed, distance):
		self.x += self.velocity * math.cos(self.yaw) * interval
		self.y += self.velocity * math.sin(self.yaw) * interval
		self.yaw += self.velocity / angle_base * math.tan(distance) * interval
		self.velocity += speed * interval
		self.x_and_yaw = self.x - ((angle_base / 2) * math.cos(self.yaw))
		self.y_and_yaw = self.y - ((angle_base / 2) * math.sin(self.yaw))

	def calc_distance(self, point_x, point_y):
		dx = self.x_and_yaw - point_x
		dy = self.y_and_yaw - point_y
		return math.hypot(dx, dy)


class States:

	def __init__(self):
		self.x = []
		self.y = []
		self.yaw = []
		self.velocities = []
		self.times = []

	def append(self, t, state: Robot):
		self.x.append(state.x)
		self.y.append(state.y)
		self.yaw.append(state.yaw)
		self.velocities.append(state.velocity)
		self.times.append(t)


def proportional_control(target_speed, robot_pos_x):
	time_distance = proportional_speed * (target_speed - robot_pos_x)

	return time_distance


class TargetCourse:

	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.old_nearest_point_index = None

	def search_target_index(self, robot):

		# To speed up nearest point search, doing it at only first time.
		if self.old_nearest_point_index is None:
			# search nearest point index
			dx = [robot.x_and_yaw - icx for icx in self.cx]
			dy = [robot.y_and_yaw - icy for icy in self.cy]
			d = np.hypot(dx, dy)
			ind = np.argmin(d)
			self.old_nearest_point_index = ind
		else:
			ind = self.old_nearest_point_index
			distance_this_index = robot.calc_distance(self.cx[ind], self.cy[ind])
			while True:
				distance_next_index = robot.calc_distance(self.cx[ind + 1], self.cy[ind + 1])
				if distance_this_index < distance_next_index:
					break
				ind = ind + 1 if (ind + 1) < len(self.cx) else ind
				distance_this_index = distance_next_index
			self.old_nearest_point_index = ind

		next_position = look_foward_gain * robot.velocity + look_ahead_distance  # update look ahead distance

		# search look ahead target point index
		while next_position > robot.calc_distance(self.cx[ind], self.cy[ind]):
			if (ind + 1) >= len(self.cx):
				break  # not exceed goal
			ind += 1

		return ind, next_position


def pure_pursuit_steer_control(robot, target_path, path_index):
	next_path_index, next_position = target_path.search_target_index(robot)

	if path_index >= next_path_index:
		next_path_index = path_index

	if next_path_index < len(target_path.cx):
		tx = target_path.cx[next_path_index]
		ty = target_path.cy[next_path_index]
	else:  # toward goal
		tx = target_path.cx[-1]
		ty = target_path.cy[-1]
		next_path_index = len(target_path.cx) - 1

	alpha = math.atan2(ty - robot.y_and_yaw, tx - robot.x_and_yaw) - robot.yaw
	distance = math.atan2(2.0 * angle_base * math.sin(alpha) / next_position, 1.0)

	return distance, next_path_index


def plot_arrow(x, y, yaw, length=1.0, width=0.5, fc="r", ec="k"):
	"""
	Plot arrow
	"""

	if not isinstance(x, float):
		for ix, iy, iyaw in zip(x, y, yaw):
			plot_arrow(ix, iy, iyaw)
	else:
		plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
				  fc=fc, ec=ec, head_width=width, head_length=width)
		plt.plot(x, y)


def main():
	#  target points
	cx = np.arange(0, 50, 0.5)
	cy = [math.sin(ix / 5.0) * ix / 2.0 for ix in cx]

	target_speed = 10.0 / 3.6  # [m/s]

	T = 100.0  # max simulation time

	# initial state
	robot = Robot(x=-0.0, y=-10.0, yaw=0.0, v=0.0)

	lastIndex = len(cx) - 1
	time = 0.0
	states = States()
	states.append(time, robot)
	target_path = TargetCourse(cx, cy)
	target_ind, _ = target_path.search_target_index(robot)

	while T >= time and lastIndex > target_ind:

		# Calc control input
		speed = proportional_control(target_speed, robot.velocity)
		distance, target_ind = pure_pursuit_steer_control(robot, target_path, target_ind)

		robot.update(speed, distance)  # Control vehicle

		time += interval
		states.append(time, robot)

		if show_animation:  # pragma: no cover
			plt.cla()
			# for stopping simulation with the esc key.
			plt.gcf().canvas.mpl_connect(
				'key_release_event',
				lambda event: [exit(0) if event.key == 'escape' else None]
			)
			plot_arrow(robot.x, robot.y, robot.yaw)

			plt.plot(cx, cy, "-r", label="target path")
			plt.plot(states.x, states.y, "-b", label="robot path")
			plt.plot(cx[target_ind], cy[target_ind], "xg", label="target")
			plt.axis("equal")
			plt.grid(True)
			plt.title("Speed[km/h]:" + str(robot.velocity * 3.6)[:4])
			plt.pause(0.001)

	# Test
	assert lastIndex >= target_ind, "Cannot goal"

	if show_animation:  # pragma: no cover
		plt.cla()
		plt.plot(cx, cy, ".r", label="target path")
		plt.plot(states.x, states.y, "-b", label="robot path")
		plt.legend()
		plt.xlabel("x[m]")
		plt.ylabel("y[m]")
		plt.axis("equal")
		plt.grid(True)

		plt.subplots(1)
		plt.plot(states.times, [iv * 3.6 for iv in states.velocities], "-r")
		plt.xlabel("Time[s]")
		plt.ylabel("Speed[km/h]")
		plt.grid(True)
		plt.show()


if __name__ == '__main__':
	print("Pure pursuit path tracking simulation start")
	main()
