import time

import pygame


def get_keys_control(tello):
	"""
		Define keys and add listener
	"""
	pygame.init()
	pygame.display.set_mode((400, 400))

	controls_key_release = {
		pygame.K_w: lambda: tello.set_speed("forward-back", 0),
		pygame.K_s: lambda: tello.set_speed("forward-back", 0),
		pygame.K_a: lambda: tello.set_speed("right-left", 0),
		pygame.K_d: lambda: tello.set_speed("right-left", 0),
		pygame.K_q: lambda: tello.set_speed("rotation", 0),
		pygame.K_e: lambda: tello.set_speed("rotation", 0),
		pygame.K_LEFT: lambda: tello.set_speed("rotation", 0),
		pygame.K_RIGHT: lambda: tello.set_speed("rotation", 0),
		pygame.K_UP: lambda: tello.set_speed("up-down", 0),
		pygame.K_DOWN: lambda: tello.set_speed("up-down", 0)
	}

	controls_key_pressed = {
		pygame.K_w: lambda: tello.set_speed("forward-back", tello.def_speed["forward-back"]),
		pygame.K_s: lambda: tello.set_speed("forward-back", -tello.def_speed["forward-back"]),
		pygame.K_a: lambda: tello.set_speed("right-left", -tello.def_speed["right-left"]),
		pygame.K_d: lambda: tello.set_speed("right-left", tello.def_speed["right-left"]),
		pygame.K_q: lambda: tello.set_speed("rotation", -tello.def_speed["rotation"]),
		pygame.K_e: lambda: tello.set_speed("rotation", tello.def_speed["rotation"]),
		pygame.K_i: lambda: tello.drone.flip_forward(),
		pygame.K_k: lambda: tello.drone.flip_back(),
		pygame.K_j: lambda: tello.drone.flip_left(),
		pygame.K_l: lambda: tello.drone.flip_right(),
		pygame.K_LEFT: lambda: tello.set_speed("rotation", -1.5 * tello.def_speed["rotation"]),
		pygame.K_RIGHT: lambda: tello.set_speed("rotation", 1.5 * tello.def_speed["rotation"]),
		pygame.K_UP: lambda: tello.set_speed("up-down", tello.def_speed["up-down"]),
		pygame.K_DOWN: lambda: tello.set_speed("up-down", -tello.def_speed["up-down"]),
		pygame.K_TAB: lambda: takeoff(tello),
		pygame.K_BACKSPACE: lambda: tello.drone.land(),
		pygame.K_p: lambda: tello.palm_land(),
		pygame.K_t: lambda: tello.toggle_tracking(),
		pygame.K_o: lambda: tello.toggle_gesture_control(),
		pygame.K_KP_ENTER: lambda: tello.take_picture(),
		pygame.K_v: lambda: key_quit(tello)
	}
	return controls_key_pressed, controls_key_release


def takeoff(tello):
	time.sleep(2)
	tello.is_flying = True
	tello.axis_speed["up-down"] = 30
	return tello.drone.takeoff()


def key_quit(tello):
	tello.toggle_tracking(False)
	tello.drone.land()
