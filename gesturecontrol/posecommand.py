import time

from simple_pid import PID


class PoseCommandRunner:
	def __init__(self, controller, log, proximity):
		self.proximity = proximity
		self.controller = controller
		self.log = log
		self.commands = self.get_commands()

	def run(self, pose):
		if pose in self.commands:
			command = self.commands[pose]
			command(self.controller, self.log)

	@staticmethod
	def go_left(controller, log):
		log.info("GOING LEFT from pose")
		controller.axis_speed["right-left"] = controller.def_speed["right-left"]

	@staticmethod
	def go_right(controller, log):
		log.info("GOING RIGHT from pose")
		controller.axis_speed["right-left"] = -controller.def_speed["right-left"]

	@staticmethod
	def go_forward(controller, log):
		log.info("GOING FORWARD from pose")
		controller.axis_speed["forward-back"] = controller.def_speed["forward-back"]

	@staticmethod
	def go_back(controller, log):
		log.info("GOING BACKWARD from pose")
		controller.axis_speed["forward-back"] = -controller.def_speed["forward-back"]

	@staticmethod
	def lock_dist(controller, log):
		# Locked distance mode
		if controller.keep_distance is None:
			if time.time() - controller.timestamp_keep_distance > controller.toggle_action_interval:
				# The first frame of a serie to activate the distance keeping
				controller.keep_distance = controller.shoulders_width
				controller.timestamp_keep_distance = time.time()
				log.info(f"KEEP DISTANCE {controller.keep_distance}")
				controller.pid_pitch = PID(0.5, 0.04, 0.3, setpoint=0, output_limits=(-50, 50))
				controller.sound_player.play("keeping distance")
		else:
			if time.time() - controller.timestamp_keep_distance > controller.toggle_action_interval:
				log.info("KEEP DISTANCE FINISHED")
				controller.sound_player.play("free")
				controller.keep_distance = None
				controller.timestamp_keep_distance = time.time()

	def initiate_palm_landing(self, controller, log):
		# Get close to the body then palm landing
		if not controller.palm_landing_approach:
			controller.toggle_tracking(tracking=True)
			controller.palm_landing_approach = True
			controller.keep_distance = self.proximity
			controller.timestamp_keep_distance = time.time()
			log.info("APPROACHING on pose")
			controller.pid_pitch = PID(0.2, 0.02, 0.1, setpoint=0, output_limits=(-45, 45))
			controller.sound_player.play("approaching")

	@staticmethod
	def land(controller, log):
		if not controller.palm_landing:
			log.info("LANDING on pose")
			controller.toggle_tracking(tracking=False)
			controller.sound_player.play("landing")
			controller.drone.land()

	@staticmethod
	def toggle_tracking(controller, log):
		log.info("TRACKING TOGGLE on pose")
		controller.toggle_tracking()

	@staticmethod
	def taking_picture(controller, log):
		controller.take_picture()

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
