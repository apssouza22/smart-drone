import time

import cv2


class InfoDisplayer:
	def __init__(self, def_color=(255, 170, 0)):
		self.def_color = def_color
		self.infos = []

	def add(self, info, color=None):
		if color is None: color = self.def_color
		self.infos.append((info, color))

	def draw(self, frame):
		i = 0
		for (info, color) in self.infos:
			cv2.putText(
				frame, info, (0, 30 + (i * 30)),
				cv2.FONT_HERSHEY_SIMPLEX,
				1.0, color, 2
			)  # lineType=30)
			i += 1

	def display_info(self, tello, frame, fps):
		self.infos = []
		fps.update()
		self.add(f"FPS {fps.get():.2f}")
		self.add(f"BAT {tello.battery}")
		self.add(f"TRACKING {'ON' if tello.tracking else 'OFF'}", (0, 255, 0) if tello.tracking else (0, 0, 255))

		if tello.is_flying:
			self.add("FLYING", (0, 255, 0))
		else:
			self.add("NOT FLYING", (0, 0, 255))

		if tello.axis_speed['rotation'] > 0:
			self.add(f"ROTATION {tello.axis_speed['rotation']}", (0, 255, 0))
		elif tello.axis_speed['rotation'] < 0:
			self.add(f"ROTATION {-tello.axis_speed['rotation']}", (0, 0, 255))
		else:
			self.add(f"ROTATION 0")

		if tello.axis_speed['right-left'] > 0:
			self.add(f"RIGHT {tello.axis_speed['right-left']}", (0, 255, 0))
		elif tello.axis_speed['right-left'] < 0:
			self.add(f"LEFT {-tello.axis_speed['right-left']}", (0, 0, 255))
		else:
			self.add(f"RIGHT 0")

		if tello.axis_speed['forward-back'] > 0:
			self.add(f"FORWARD {tello.axis_speed['forward-back']}", (0, 255, 0))
		elif tello.axis_speed['forward-back'] < 0:
			self.add(f"BACKWARD {-tello.axis_speed['forward-back']}", (0, 0, 255))
		else:
			self.add(f"FORWARD 0")

		if tello.axis_speed['up-down'] > 0:
			self.add(f"UP {tello.axis_speed['up-down']}", (0, 255, 0))
		elif tello.axis_speed['up-down'] < 0:
			self.add(f"DOWN {-tello.axis_speed['up-down']}", (0, 0, 255))
		else:
			self.add(f"UP 0")

		if tello.use_gesture_control:
			self.add(f"POSE: {tello.use_gesture_control}", (0, 255, 0) if tello.use_gesture_control else (255, 170, 0))
		if tello.keep_distance:
			self.add(f"Target distance: {tello.keep_distance} - curr: {tello.shoulders_width}", (0, 255, 0))
		if tello.timestamp_take_picture:
			self.add("Taking a picture", (0, 255, 0))
		if tello.palm_landing:
			self.add("Palm landing...", (0, 255, 0))
		if tello.palm_landing_approach:
			self.add("In approach for palm landing...", (0, 255, 0))
		if tello.tracking and not tello.tracker.body_in_prev_frame and time.time() - tello.timestamp_no_body > 0.5:
			self.add("Searching...", (0, 255, 0))
		if tello.scheduled_takeoff:
			seconds_left = int(tello.scheduled_takeoff - time.time())
			self.add(f"Takeoff in {seconds_left}s")

		self.draw(frame)
		return frame
