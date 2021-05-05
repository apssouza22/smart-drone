"""

Relies on tellopy (for interaction with the Tello drone) and Openpose (for body detection and pose recognition)

I started from: https://github.com/Ubotica/telloCV/blob/master/telloCV.py

"""
import logging
import sys
import time

from djitellopy import tello as drone
from simple_pid import PID

from common.keypress import is_key_pressed, kp_init
from airselfie.cameramorse import CameraMorse
from airselfie.posedetectorwrapper import *
from airselfie.soundplayer import SoundPlayer, Tone
from airselfie.info import InfoDisplayer
from airselfie.keycontrol import get_keys_control
from airselfie.posecheck import PoseChecker
from airselfie.posecommand import PoseCommandRunner
from airselfie.tracking import PersonTracker

log = logging.getLogger("TellOpenpose")


class TelloController(object):
	"""
	TelloController builds keyboard controls on top of TelloPy as well
	as generating images from the video stream and enabling opencv support
	"""

	def __init__(
			self,
			log_level=None
	):
		self.toggle_action_interval = 2  # buffer in seconds for toggle actions
		self.pose = None
		self.log_level = log_level
		self.is_flying = False
		self.drone = drone.Tello()
		self.axis_speed = {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}

		self.cmd_axis_speed = {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}
		self.prev_axis_speed = self.axis_speed.copy()
		self.def_speed = {"rotation": 50, "right-left": 35, "forward-back": 35, "up-down": 80}
		self.rotation = 0
		self.toggle_tracking_timestamp = time.time() - 3
		self.tracking_after_takeoff = False
		self.tracking = False
		self.wait_before_tracking = None
		self.keep_distance = None
		self.palm_landing = False
		self.palm_landing_approach = False
		self.rotation_to_consume = 0
		self.timestamp_keep_distance = time.time()
		self.timestamp_take_picture = None
		self.throw_ongoing = False
		self.scheduled_takeoff = None
		self.timestamp_no_body = time.time()
		self.rotation_to_consume = 0
		self.set_logging(log_level)
		self.init_drone()
		self.init_sounds()
		self.init_keyboard_controls()
		self.start_time = time.time()
		self.use_gesture_control = True
		self.is_pressed = False
		self.battery = self.drone.get_battery()
		self.op = PoseDetectorWrapper()
		self.morse = CameraMorse(display=False)
		self.morse.define_command("-", self.delayed_takeoff)
		self.fps = FPS()
		self.tracker = PersonTracker(log)

		# self.delayed_takeoff()
		self.toggle_tracking(tracking=True)

	def set_logging(self, log_level):
		# Logging
		self.log_level = log_level
		if log_level is not None:
			if log_level == "info":
				log_level = logging.INFO
			elif log_level == "debug":
				log_level = logging.DEBUG
			log.setLevel(log_level)
			ch = logging.StreamHandler(sys.stdout)
			ch.setLevel(log_level)
			ch.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S"))
			log.addHandler(ch)

	def init_drone(self):
		"""
			Connect to the drone, start streaming and subscribe to events
		"""
		self.drone.connect()
		self.drone.streamon()

	def init_sounds(self):
		self.sound_player = SoundPlayer()
		self.sound_player.load("approaching", "airselfie/sounds/approaching.ogg")
		self.sound_player.load("keeping distance", "airselfie/sounds/keeping_distance.ogg")
		self.sound_player.load("landing", "airselfie/sounds/landing.ogg")
		self.sound_player.load("palm landing", "airselfie/sounds/palm_landing.ogg")
		self.sound_player.load("taking picture", "airselfie/sounds/taking_picture.ogg")
		self.sound_player.load("free", "airselfie/sounds/free.ogg")
		self.sound_player.load("bonjour", "airselfie/sounds/bonjour.ogg")
		self.sound_player.load("tracking", "airselfie/sounds/hello.ogg")
		self.tone = Tone()

	def keyboard_listener(self):
		self.set_speed("forward-back", 0),
		self.set_speed("right-left", 0)
		self.set_speed("rotation", 0)
		self.set_speed("up-down", 0)

		for keyname in self.controls_keypress:
			if is_key_pressed(keyname):
				self.controls_keypress[keyname]()

	def set_speed(self, axis, speed):
		log.info(f"set speed {axis} {speed}")
		self.cmd_axis_speed[axis] = speed

	def init_keyboard_controls(self):
		"""
			Define keys and add listener
		"""
		kp_init()
		self.controls_keypress = get_keys_control(self)

	def process_frame(self, frame):
		"""
			Analyze the frame and return the frame with information (HUD, openpose skeleton) drawn on it
		"""

		# Is there a scheduled takeoff ?
		if self.scheduled_takeoff and time.time() > self.scheduled_takeoff:
			self.scheduled_takeoff = None
			self.drone.takeoff()
			self.axis_speed["up-down"] = 30

		self.axis_speed = self.cmd_axis_speed.copy()

		# If we are on the point to take a picture, the tracking is temporarily desactivated (2s)
		if self.timestamp_take_picture:
			if time.time() - self.timestamp_take_picture > 2:
				self.timestamp_take_picture = None
				self.take_picture(frame)

			self.send_drone_command()
			return self.write_info(frame)

		self.set_current_position()
		self.morse_eval(frame)
		self.pose_eval(frame)
		self.send_drone_command()
		return self.write_info(frame)

	def pose_eval(self, frame):
		"""Call to pose detection"""
		if not self.use_gesture_control:
			return

		# Our target is the person whose index is 0 in pose_kps
		self.tracker.target = None
		self.pose = None
		height, width, _ = frame.shape
		proximity = int(width / 2.6)
		self.op.eval(frame)

		if len(self.op.pose_kps) > 0:
			self.op.draw_body(frame)
			# We found a body, so we can cancel the exploring 360
			self.rotation_to_consume = 0

			# Do we recognize a predefined pose ?
			check = PoseChecker(self)
			self.pose = check.get_pose(frame)

			if self.pose:
				pose_command = PoseCommandRunner(self, log, proximity)
				pose_command.run(self.pose)

			self.tracker.get_best_body_position(self, width, height)

		if self.tracking:
			if self.tracker.target:
				self.tracker.track_target(self, frame)
			else:
				self.tracker.find_target(self)

	def morse_eval(self, frame):
		"""We are not flying, we check a potential morse code"""
		if not self.is_flying:
			pressing, detected = self.morse.eval(frame)
			if self.is_pressed and not pressing:
				self.tone.off()
			if not self.is_pressed and pressing:
				self.tone.on()
			self.is_pressed = pressing

	def set_current_position(self):
		"""If we are doing a 360, where are we in our 360 ?"""
		if self.rotation_to_consume > 0:
			consumed = self.rotation - self.prev_rotation
			self.prev_rotation = self.rotation
			if consumed < 0: consumed += 360
			self.rotation_consumed += consumed
			if self.rotation_consumed > self.rotation_to_consume:
				self.rotation_to_consume = 0
				self.axis_speed["rotation"] = 0
			else:
				self.axis_speed["rotation"] = self.def_speed["rotation"]

	def send_drone_command(self):
		for axis, speed in self.axis_speed.items():
			if self.axis_speed[axis] is not None and self.axis_speed[axis] != self.prev_axis_speed[axis]:
				self.prev_axis_speed[axis] = self.axis_speed[axis]
			else:
				# This line is necessary to display current values in 'self.write_hud'
				self.axis_speed[axis] = self.prev_axis_speed[axis]

		self.drone.send_rc_control(
			int(self.axis_speed["right-left"]),
			int(self.axis_speed["forward-back"]),
			int(self.axis_speed["up-down"]),
			int(self.axis_speed["rotation"])
		)

	def write_info(self, frame):
		"""
			Draw drone info on frame
		"""
		info = InfoDisplayer()
		return info.display_info(self, frame)

	def take_picture(self, frame):
		"""
			Tell drone to take picture, image sent to file handler
		"""

	# TODO implement take picture

	def palm_land(self):
		"""
			Tell drone to land
		"""
		self.palm_landing = True
		self.sound_player.play("palm landing")
		self.drone.palm_land()

	def delayed_takeoff(self, delay=5):
		self.scheduled_takeoff = time.time() + delay
		self.tracking_after_takeoff = True

	def clockwise_degrees(self, degrees):
		self.rotation_to_consume = degrees
		self.rotation_consumed = 0
		self.prev_rotation = self.rotation

	def toggle_gesture_control(self):
		self.use_gesture_control = not self.use_gesture_control
		if not self.use_gesture_control:
			self.toggle_tracking(tracking=False)
		log.info('OPENPOSE ' + ("ON" if self.use_gesture_control else "OFF"))

	def toggle_tracking(self, tracking=None):
		"""
			If tracking is None, toggle value of self.tracking
			Else self.tracking take the same value as tracking
		"""
		if time.time() - self.toggle_tracking_timestamp < self.toggle_action_interval:
			return

		self.toggle_tracking_timestamp = time.time()
		self.sound_player.play("tracking")
		if tracking is None:
			self.tracking = not self.tracking
		else:
			self.tracking = tracking
		if self.tracking:
			log.info("ACTIVATE TRACKING")
			self.sound_player.play()
			# Needs openpose
			self.use_gesture_control = True
			# Start an explarotary 360
			# self.clockwise_degrees(360)
			# Init a PID controller for the rotation and one for the throttle
			self.pid_rotation = PID(0.25, 0, 0, setpoint=0, output_limits=(-100, 100))
			self.pid_throttle = PID(0.4, 0, 0, setpoint=0, output_limits=(-80, 100))
		else:
			self.axis_speed = {"rotation": 0, "right-left": 0, "forward-back": 0, "up-down": 0}
			self.keep_distance = None
