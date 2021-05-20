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
	def take_picture(tello, log):
		# We trigger the associated action
		log.info(f"pose detected : {tello.pose}")
		# Take a picture in 1 second
		if tello.timestamp_take_picture is None:
			log.info("Take a picture in 1 second")
			tello.timestamp_take_picture = time.time()
			tello.sound_player.play("taking picture")

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
				# tello.graph_distance = RollingGraph(window_name="Distance", y_max=500, threshold=tello.keep_distance, waitKey=False)
				tello.sound_player.play("keeping distance")
		else:
			if time.time() - tello.timestamp_keep_distance > tello.toggle_action_interval:
				log.info("KEEP DISTANCE FINISHED")
				tello.sound_player.play("free")
				tello.keep_distance = None
				tello.timestamp_keep_distance = time.time()

	def palm_land(self, tello, log):
		# Get close to the body then palm landing
		if not tello.palm_landing_approach:
			tello.palm_landing_approach = True
			tello.keep_distance = self.proximity
			tello.timestamp_keep_distance = time.time()
			log.info("APPROACHING on pose")
			tello.pid_pitch = PID(0.2, 0.02, 0.1, setpoint=0, output_limits=(-45, 45))
			tello.sound_player.play("approaching")

	@staticmethod
	def land(tello, log):
		if time.time() - tello.toggle_tracking_timestamp < tello.toggle_action_interval:
			return

		tello.toggle_tracking_timestamp = time.time()

		if not tello.palm_landing:
			log.info("LANDING on pose")
			tello.toggle_tracking(tracking=False)
			tello.drone.land()
			tello.sound_player.play("landing")
			tello.is_flying = False

	@staticmethod
	def toggle_tracking(tello, log):
		log.info("TRACKING TOGGLE on pose")
		tello.toggle_tracking()

	def get_commands(self):
		return {
			"RIGHT_HAND_FINGERS_UP_0": self.land,
			"RIGHT_HAND_FINGERS_UP_1": self.go_left,
			"RIGHT_HAND_FINGERS_UP_2": self.go_right,
			# "RIGHT_HAND_FINGERS_UP_5": self.palm_land,
			"RIGHT_HAND_FINGERS_UP_4": self.lock_dist,
			"LEFT_HAND_FINGERS_UP_0": self.toggle_tracking,
			"LEFT_HAND_FINGERS_UP_1": self.go_forward,
			"LEFT_HAND_FINGERS_UP_2": self.go_back,

			# Commands disabled at the moment
			"HANDS_ON_NECK": self.take_picture,
			"HANDS_ON_EARS": self.take_picture,
			"LEFT_HAND_ON_RIGHT_EAR": self.land,
			"RIGHT_HAND_ON_LEFT_EAR": self.palm_land,
			"CLOSE_HANDS_UP": self.lock_dist,
			"LEFT_ARM_UP_OPEN": self.go_back,
			"LEFT_ARM_UP_CLOSED": self.go_forward,
			"RIGHT_ARM_UP_OPEN": self.go_right,
			"RIGHT_ARM_UP_CLOSED": self.go_left,
		}
