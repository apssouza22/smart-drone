"""
Use the Tello drone as an "selfie air stick"

This program control Tello drone https://www.harveynorman.ie/cameras-drones/drones-ireland/all-drones/rryze-tello-drone-powered-by-dji.html
The control is based on Keyboard and hand gestures
The body detection is done with MediaPipe

Inspired by https://github.com/geaxgx/tello-openpose

"""
from airselfie.controller import *


def get_frame(drone_camera, tello):
	if drone_camera:
		return lambda: tello.drone.get_frame_read().frame

	cap = cv2.VideoCapture(0)
	return lambda: cap.read()[1]


def main(drone_camera=True, enable_keyboard=False, log_level=None):
	"""
		Main function
		drone_camera = False will use your computer camera. Useful for developemnt
		enable_keyboard = True will enable control the drone with the key board. This will reduce considerably the FPS
	"""
	tello = TelloController(log_level=log_level)
	if enable_keyboard:
		tello.init_keyboard_controls()

	frame_skip = 300
	total_frames = 0
	skip_frames = 10
	read_frame_fn = get_frame(drone_camera, tello)

	while True:
		if 0 < frame_skip:
			frame_skip = frame_skip - 1
			continue

		if total_frames % skip_frames != 0:
			continue

		if enable_keyboard:
			tello.keyboard_listener()

		frame = read_frame_fn()
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
		frame = cv2.resize(frame, (640, 480))
		frame = tello.process_frame(frame)
		tello.sound_player.play()
		tello.fps.update()
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
		cv2.imshow('My image', frame)
		cv2.waitKey(1)


if __name__ == '__main__':
	main(False, True, None)
