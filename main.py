"""
Smart drone
"""

import cv2

from common.controller import TelloEngine
from common.drone import Drone
from common.fps import FPS
from common.info import InfoDisplayer
from webserver.manager import WebControlManager

frame_skip = 300


def skip_frame():
	global frame_skip
	total_frames = 0
	skip_frames = 10
	if 0 < frame_skip:
		frame_skip = frame_skip - 1
		return True

	if total_frames % skip_frames != 0:
		return True

	return False


def main(mock_drone=True, enable_web=False, enable_socket=False, log_level=None):
	"""
		Main function
		mock_drone = False will use your computer camera
		enable_web = start a web server with streaming video and remote control
		enable_socket = start a socket server to send the current drone position
	"""
	drone = Drone(mock_drone)
	drone.start()

	engine = TelloEngine(drone, log_level=log_level)
	fps = FPS()
	info = InfoDisplayer()
	web_control = WebControlManager(enable_web, enable_socket, engine.pygame_screen)
	web_control.start_http()
	web_control.start_socket()

	while True:
		if skip_frame():
			continue
		engine.pygame_screen.watch_events()
		frame = drone.get_frame()
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
		frame = cv2.resize(frame, (640, 480))
		frame = engine.process(frame)
		engine.sound_player.play()
		frame = info.display_info(engine, frame, fps)
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
		web_control.send_frame(frame)
		web_control.send_msg(str(engine.drone.drone_locator.x) + "-" + str(engine.drone.drone_locator.y))
		cv2.imshow('My image', frame)
		cv2.waitKey(1)


if __name__ == '__main__':
	main(True, True, False, None)
