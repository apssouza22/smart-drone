"""
Smart drone
"""
import cv2

from common.controller import TelloEngine
from common.drone import Drone
from common.fps import FPS
from common.info import InfoDisplayer

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


def main(mock_drone=True, log_level=None):
	"""
		Main function
		mock_drone = False will use your computer camera. Useful for development
	"""
	drone = Drone(mock_drone)
	drone.start()

	engine = TelloEngine(drone, log_level=log_level)
	fps = FPS()
	info = InfoDisplayer()

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
		cv2.imshow('My image', frame)
		cv2.waitKey(1)


if __name__ == '__main__':
	main(True, None)
