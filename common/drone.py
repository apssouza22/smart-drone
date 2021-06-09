import cv2
from djitellopy import tello as drone


class Drone:
	is_flying = False

	def __init__(self, mock: bool):
		self.sdk = drone.Tello()
		self.mock = mock
		self.video_stream = self.start_stream()

	def start(self):
		if self.mock:
			print("Starting mocked drone")
			return

		self.sdk.connect()
		self.sdk.streamon()

	def get_frame(self):
		return self.video_stream()

	def start_stream(self):
		if not self.mock:
			return lambda: self.sdk.get_frame_read().frame

		cap = cv2.VideoCapture(0)
		return lambda: cap.read()[1]

	def get_battery(self):
		self.sdk.get_battery()

	def takeoff(self):
		self.is_flying = True
		self.sdk.takeoff()

	def land(self):
		self.is_flying = False
		self.sdk.land()

	def update(self, right_left, forward_back, up_down, rotation):
		self.sdk.send_rc_control(right_left, forward_back, up_down, rotation)
