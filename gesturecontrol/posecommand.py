import time

from simple_pid import PID


class PoseCommandRunner:
	def __init__(self, tello, log, proximity):
		self.proximity = proximity
		self.tello = tello
		self.log = log
		self.commands = self.get_commands()

	def run(self, pose):
		if pose in self.commands:
			command = self.commands[pose]
			command(self.tello, self.log)

	@staticmethod
	def go_left(tello, log):
		log.info("GOING LEFT from pose")
		tello.axis_speed["right-left"] = tello.def_speed["right-left"]

	@staticmethod
	def go_right(tello, log):
		log.info("GOING RIGHT from pose")
		tello.axis_speed["right-left"] = -tello.def_speed["right-left"]

	@staticmethod
	def go_forward(tello, log):
		log.info("GOING FORWARD from pose")
		tello.axis_speed["forward-back"] = tello.def_speed["forward-back"]

	@staticmethod
	def go_back(tello, log):
		log.info("GOING BACKWARD from pose")
		tello.axis_speed["forward-back"] = -tello.def_speed["forward-back"]

	@staticmethod
	def lock_dist(tello, log):
		# Locked distance mode
		if tello.keep_distance is None:
			if time.time() - tello.timestamp_keep_distance > tello.toggle_action_interval:
				# The first frame of a serie to activate the distance keeping
				tello.keep_distance = tello.shoulders_width
				tello.timestamp_keep_distance = time.time()
				log.info(f"KEEP DISTANCE {tello.keep_distance}")
				tello.pid_pitch = PID(0.5, 0.04, 0.3, setpoint=0, output_limits=(-50, 50))
				tello.sound_player.play("keeping distance")
		else:
			if time.time() - tello.timestamp_keep_distance > tello.toggle_action_interval:
				log.info("KEEP DISTANCE FINISHED")
				tello.sound_player.play("free")
				tello.keep_distance = None
				tello.timestamp_keep_distance = time.time()

	def initiate_palm_landing(self, engine, log):
		# Get close to the body then palm landing
		if not engine.palm_landing_approach:
			engine.toggle_tracking(tracking=True)
			engine.palm_landing_approach = True
			engine.keep_distance = self.proximity
			engine.timestamp_keep_distance = time.time()
			log.info("APPROACHING on pose")
			engine.pid_pitch = PID(0.2, 0.02, 0.1, setpoint=0, output_limits=(-45, 45))
			engine.sound_player.play("approaching")

	@staticmethod
	def land(tello, log):
		if not tello.palm_landing:
			log.info("LANDING on pose")
			tello.toggle_tracking(tracking=False)
			tello.sound_player.play("landing")
			tello.drone.land()

	@staticmethod
	def toggle_tracking(tello, log):
		log.info("TRACKING TOGGLE on pose")
		tello.toggle_tracking()

	@staticmethod
	def taking_picture(tello, log):
		tello.take_picture()

	def get_commands(self):
		return {
			"RIGHT_HAND_FINGERS_UP_0": self.lock_dist,
			"RIGHT_HAND_FINGERS_UP_1": self.go_left,
			"RIGHT_HAND_FINGERS_UP_2": self.go_right,
			"LEFT_HAND_FINGERS_UP_0": self.toggle_tracking,
			"LEFT_HAND_FINGERS_UP_1": self.go_forward,
			"LEFT_HAND_FINGERS_UP_2": self.go_back,
			"BOTH_HAND_FINGERS_UP_0": self.land,
			"BOTH_HAND_FINGERS_UP_1": self.taking_picture,
			"BOTH_HAND_FINGERS_UP_2": self.initiate_palm_landing,

			# Commands disabled at the moment
			# "HANDS_ON_NECK": self.take_picture,
			# "HANDS_ON_EARS": self.take_picture,
			# "LEFT_HAND_ON_RIGHT_EAR": self.land,
			# "RIGHT_HAND_ON_LEFT_EAR": self.palm_land,
			# "CLOSE_HANDS_UP": self.lock_dist,
			# "LEFT_ARM_UP_OPEN": self.go_back,
			# "LEFT_ARM_UP_CLOSED": self.go_forward,
			# "RIGHT_ARM_UP_OPEN": self.go_right,
			# "RIGHT_ARM_UP_CLOSED": self.go_left,
		}
