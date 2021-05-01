import time

import cv2


class PersonTracker:
	"""Person tracking"""

	def __init__(self, log):
		self.log = log
		# When in trackin mode, but no body is detected in current frame,
		# we make the drone rotate in the hope to find some body
		# The rotation is done in the same direction as the last rotation done
		self.body_in_prev_frame = True
		self.last_rotation_is_cw = True
		self.timestamp_no_body = time.time()
		self.ref_x = None
		self.ref_y = None
		self.target = None

	def find_target(self, tello):
		"""If in tracking mode and no body detected, the drone will try to find a body"""

		if self.body_in_prev_frame:
			self.timestamp_no_body = time.time()
			self.body_in_prev_frame = False
			tello.axis_speed["up-down"] = tello.prev_axis_speed["up-down"]
			tello.axis_speed["rotation"] = tello.prev_axis_speed["rotation"]
		else:
			if time.time() - self.timestamp_no_body < 1:
				print("NO BODY SINCE < 1", tello.axis_speed, tello.prev_axis_speed)
				tello.axis_speed["up-down"] = tello.prev_axis_speed["up-down"]
				tello.axis_speed["rotation"] = tello.prev_axis_speed["rotation"]
			else:
				self.log.debug("NO BODY detected for 1s -> rotate")
				tello.axis_speed["rotation"] = tello.def_speed["rotation"] * (1 if self.last_rotation_is_cw else -1)

	def track_target(self, tello, frame):
		"""If in tracking mode, the drone will try to track the target"""

		self.body_in_prev_frame = True
		# We draw an arrow from the reference point to the body part we are targeting
		h, w, _ = frame.shape
		xoff = int(self.target[0] - self.ref_x)
		yoff = int(self.ref_y - self.target[1])
		cv2.circle(frame, (self.ref_x, self.ref_y), 15, (250, 150, 0), 1, cv2.LINE_AA)
		cv2.arrowedLine(frame, (self.ref_x, self.ref_y), self.target, (250, 150, 0), 6)
		# The PID controllers calculate the new speeds for rotation and throttle
		tello.axis_speed["rotation"] = int(-tello.pid_rotation(xoff))
		self.log.debug(f"xoff: {xoff} - speed_rotation: {tello.axis_speed['rotation']}")
		self.last_rotation_is_cw = tello.axis_speed["rotation"] > 0
		tello.axis_speed["up-down"] = int(-tello.pid_throttle(yoff))
		self.log.debug(f"yoff: {yoff} - speed_throttle: {tello.axis_speed['up-down']}")
		# If in locke distance mode
		if tello.keep_distance and tello.shoulders_width:
			if tello.palm_landing_approach and tello.shoulders_width > tello.keep_distance:
				# The drone is now close enough to the body
				# Let's do the palm landing
				self.log.info("PALM LANDING after approaching")
				tello.palm_landing_approach = False
				tello.toggle_tracking(tracking=False)
				tello.palm_land()
			else:
				tello.axis_speed["forward-back"] = int(tello.pid_pitch(tello.shoulders_width - tello.keep_distance))
				self.log.debug(f"Target distance: {tello.keep_distance} - cur: {tello.shoulders_width} -speed_forward-back: {tello.axis_speed['forward-back']}")

	def get_best_body_position(self, tello, w, h):
		# In tracking mode, we track a specific body part (an openpose keypoint):
		# the nose if visible, otherwise the neck, otherwise the midhip
		# The tracker tries to align that body part with the reference point (ref_x, ref_y)
		self.target = tello.op.get_body_kp("nose")
		if self.target is not None:
			self.ref_x = int(w / 2)
			self.ref_y = int(h * 0.35)
			return

		self.target = tello.op.get_body_kp("neck")
		if self.target is not None:
			self.ref_x = int(w / 2)
			self.ref_y = int(h / 2)
			return

		self.target = tello.op.get_body_kp("mid_hip")
		if self.target is not None:
			self.ref_x = int(w / 2)
			self.ref_y = int(0.75 * h)
