import os
import time

import numpy
import pygame

from common.drone import Drone
from pathplan.pathplanning import save_path_plan


class PyGameScreen:

	def __init__(self, tello):
		self.controls_keypress, self.controls_keyrelease = get_keys_control(tello)
		self.screen = self.init_pygame_screen()
		self.listeners = {}
		self.path_wp = []
		self.index = 0
		self.plan_map_opened = False

	def load_background(self, img=None):
		if img is None:
			image = pygame.image.load("pathplan/house.png")
		else:
			image = self.cvimage_to_pygame(img)

		image = pygame.transform.rotozoom(image, 0, 1)
		rect = image.get_rect()
		rect.left, rect.top = [0, 0]
		self.screen.blit(image, rect)
		pygame.display.update()

	@staticmethod
	def cvimage_to_pygame(image):
		"""Convert cvimage into a pygame image"""
		return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")

	@staticmethod
	def init_pygame_screen():
		pygame.init()
		screen = pygame.display.set_mode([720, 720])
		screen.fill((255, 255, 255))
		return screen

	def add_listener(self, fn, event):
		self.listeners[event] = fn

	def watch_events(self):
		for event in pygame.event.get():
			if event.type in self.listeners:
				self.listeners[event.type](event)

	def add_listeners(self):
		self.add_listener(self.mouse_button_down_listener, pygame.MOUSEBUTTONDOWN)
		self.add_listener(self.keypress_listener, pygame.KEYDOWN)
		self.add_listener(self.keyrelease_listener, pygame.KEYUP)
		self.add_listener(self.quit_listener, pygame.QUIT)

	def mouse_button_down_listener(self, event):
		if not self.plan_map_opened:
			return
		pos = pygame.mouse.get_pos()
		self.path_wp.append(pos)
		if self.index > 0:
			pygame.draw.line(self.screen, (255, 0, 0), self.path_wp[self.index - 1], pos, 2)
		self.index += 1
		pygame.display.update()

	def keypress_listener(self, event):
		if event.key in self.controls_keypress:
			self.controls_keypress[event.key]()

	def keyrelease_listener(self, event):
		if event.key in self.controls_keyrelease:
			self.controls_keyrelease[event.key]()

	def quit_listener(self, event):
		save_path_plan(self.path_wp)
		self.plan_map_opened = False
		img = numpy.zeros((1000, 800, 3), numpy.uint8)
		self.load_background(img)


def get_keys_control(tello):
	"""
		Define keys and add listener
	"""
	controls_key_release = {
		pygame.K_w: lambda: tello.set_speed("forward-back", 0),
		pygame.K_s: lambda: tello.set_speed("forward-back", 0),
		pygame.K_a: lambda: tello.set_speed("right-left", 0),
		pygame.K_d: lambda: tello.set_speed("right-left", 0),

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

		pygame.K_LEFT: lambda: tello.set_speed("rotation", -1.5 * tello.def_speed["rotation"]),
		pygame.K_RIGHT: lambda: tello.set_speed("rotation", 1.5 * tello.def_speed["rotation"]),
		pygame.K_UP: lambda: tello.set_speed("up-down", tello.def_speed["up-down"]),
		pygame.K_DOWN: lambda: tello.set_speed("up-down", -tello.def_speed["up-down"]),

		pygame.K_TAB: lambda: take_off(tello.drone),
		pygame.K_BACKSPACE: lambda: tello.drone.land(),
		pygame.K_KP_ENTER: lambda: tello.take_picture(),

		pygame.K_p: lambda: tello.open_path_panning(),
		pygame.K_t: lambda: tello.toggle_tracking(),
		pygame.K_g: lambda: tello.toggle_gesture_control(),
		pygame.K_v: lambda: key_quit(tello),
	}
	return controls_key_pressed, controls_key_release


def take_off(drone: Drone):
	time.sleep(2)
	return drone.takeoff()


def key_quit(tello):
	tello.toggle_tracking(False)
	tello.drone.land()
