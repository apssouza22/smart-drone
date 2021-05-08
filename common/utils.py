import math

import pygame


def get_keys_touched():
	keys_pressed = []
	keys_released = []
	for event in pygame.event.get():
		# check if the event is the X button
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.KEYDOWN:
			keys_pressed.append(event.key)

		if event.type == pygame.KEYUP:
			keys_released.append(event.key)
	return keys_pressed, keys_released


def get_dist_btw_pos(pos0, pos1):
	"""
	Get distance between 2 position.
	"""
	x = abs(pos0[0] - pos1[0])
	y = abs(pos0[1] - pos1[1])
	return math.hypot(x, y)
