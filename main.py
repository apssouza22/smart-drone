"""
Smart drone
"""
import cv2

from common.controller import TelloEngine
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


def get_frame(drone_camera, tello):
	if drone_camera:
		return lambda: tello.drone_sdk.get_frame_read().frame

	cap = cv2.VideoCapture(0)
	return lambda: cap.read()[1]


def main(drone_camera=True, log_level=None):
	"""
		Main function
		drone_camera = False will use your computer camera. Useful for development
	"""
	engine = TelloEngine(log_level=log_level)
	read_frame_fn = get_frame(drone_camera, engine)
	fps = FPS()
	info = InfoDisplayer()

	while True:
		if skip_frame():
			continue
		engine.pygame_screen.watch_events()
		frame = read_frame_fn()
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
