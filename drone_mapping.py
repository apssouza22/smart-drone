from time import sleep

from common.utils import *

drone_speed = 15
drone_rotation_speed = 50


###############################################

kp.init()
drone_conn = tello.Tello()
drone_conn.connect()
print(drone_conn.get_battery())

mapping = DroneMapping()
mapping.draw_path()

while True:
	if kp.is_key_pressed("q"): drone_conn.land(); sleep(3)
	if kp.is_key_pressed("e"): drone_conn.takeoff()

	control = handle_keyboard_input(
		drone_speed,
		drone_rotation_speed
	)

	drone_conn.send_rc_control(control.left_right, control.forward_back, control.up_down, control.rotation)

	if control.has_command():
		mapping.translate_drone_command(control)
		sleep(mapping.interval)
		mapping.draw_path()

	cv2.waitKey(1)
