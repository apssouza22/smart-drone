def get_keys_control(tello):
	"""
		Define keys and add listener
	"""

	def key_quit():
		tello.toggle_tracking(False)
		tello.drone.land()



	controls_keypress_QWERTY = {
		'w': lambda: tello.set_speed("forward-back", tello.def_speed["forward-back"]),
		's': lambda: tello.set_speed("forward-back", -tello.def_speed["forward-back"]),
		'a': lambda: tello.set_speed("right-left", -tello.def_speed["right-left"]),
		'd': lambda: tello.set_speed("right-left", tello.def_speed["right-left"]),
		'q': lambda: tello.set_speed("rotation", -tello.def_speed["rotation"]),
		'e': lambda: tello.set_speed("rotation", tello.def_speed["rotation"]),
		'i': lambda: tello.drone.flip_forward(),
		'k': lambda: tello.drone.flip_back(),
		'j': lambda: tello.drone.flip_left(),
		'l': lambda: tello.drone.flip_right(),
		'LEFT': lambda: tello.set_speed("rotation", -1.5 * tello.def_speed["rotation"]),
		'RIGHT': lambda: tello.set_speed("rotation", 1.5 * tello.def_speed["rotation"]),
		'UP': lambda: tello.set_speed("up-down", tello.def_speed["up-down"]),
		'DOWN': lambda: tello.set_speed("up-down", -tello.def_speed["up-down"]),
		'TAB': lambda: tello.drone.takeoff(),
		'BACKSPACE': lambda: tello.drone.land(),
		'p': lambda: tello.palm_land(),
		't': lambda: tello.toggle_tracking(),
		'o': lambda: tello.toggle_gesture_control(),
		# 'ENTER': lambda: tello.take_picture(),
		'v': lambda: key_quit(),
		'c': lambda: tello.clockwise_degrees(360),
	}
	return controls_keypress_QWERTY
