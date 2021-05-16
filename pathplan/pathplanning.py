import pygame
import json
import math

from common.utils import get_dist_btw_pos


def save_path_plan(path_wp):
	"""
	Compute the waypoints (distance and angle).
	"""
	# Append first pos ref. (dummy)
	path_wp.insert(0, (path_wp[0][0], path_wp[0][1] - 10))

	path_dist_cm = []
	path_dist_px = []
	path_angle = []
	path_angle_dir = []

	for index in range(len(path_wp)):
		# Skip the first and second index.
		if index > 1:
			dist_px = get_dist_btw_pos(path_wp[index - 1], path_wp[index])
			dist_cm = dist_px * MAP_SIZE_COEFF
			path_dist_cm.append(dist_cm)
			path_dist_px.append(dist_px)

		if index == 0:
			path_angle.append(0)
			path_angle_dir.append("right")

		# Skip the first and last index.
		if index > 1 and index < (len(path_wp) - 1):
			angle = get_angle_btw_line(path_wp[index - 1], path_wp[index], path_wp[index + 1])
			angle_dir = get_angle_direction(path_wp[index - 1], path_wp[index + 1])
			path_angle.append(angle)
			path_angle_dir.append(angle_dir)

	"""
	Save waypoints into JSON file.
	"""
	waypoints = []
	for index in range(len(path_dist_cm)):
		waypoints.append({
			"dist_cm": path_dist_cm[index],
			"dist_px": path_dist_px[index],
			"angle_deg": path_angle[index],
			"angle_dir": path_angle_dir[index]
		})

	# Save to JSON file.
	f = open('waypoint.json', 'w+')
	path_wp.pop(0)
	json.dump({
		"wp": waypoints,
		"pos": path_wp
	}, f, indent=4)
	f.close()


def get_angle_direction(pos0, pos2):
	x0, y0 = pos0[0], pos0[1]
	x1, y1 = pos2[0], pos2[1]
	if x0 < x1:
		if y0 < y1:
			return "right"
		else:
			return "right"

	if y0 < y1:
		return "left"
	return "right"


def get_angle_btw_line(pos0, pos1, pos2):
	"""
	Get angle between two lines respective to 'posref'
	NOTE: using dot product calculation.
	"""
	ax = pos1[0] - pos0[0]
	ay = pos1[1] - pos0[1]
	bx = pos1[0] - pos2[0]
	by = pos1[1] - pos2[1]
	# Get dot product of pos0 and pos1.
	_dot = (ax * bx) + (ay * by)
	# Get magnitude of pos0 and pos1.
	_magA = math.sqrt(ax ** 2 + ay ** 2)
	_magB = math.sqrt(bx ** 2 + by ** 2)
	_rad = math.acos(_dot / (_magA * _magB))
	# Angle in degrees.
	angle = (_rad * 180) / math.pi
	return int(angle)


"""
how many pixel = actual distance in cm
70px = 360cm --> 360/70 = MAP_SIZE_COEFF
"""
MAP_SIZE_COEFF = 5.14

if __name__ == '__main__':
	pygame.init()
	screen = pygame.display.set_mode([720, 720])
	screen.fill((255, 255, 255))
	running = True

	"""
	Main capturing mouse program.
	"""
	# Load background image.
	image = pygame.image.load('house.png')
	image = pygame.transform.rotozoom(image, 0, 1)
	rect = image.get_rect()
	rect.left, rect.top = [0, 0]
	screen.blit(image, rect)

	path_wp = []
	index = 0
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				path_wp.append(pos)
				if index > 0:
					pygame.draw.line(screen, (255, 0, 0), path_wp[index - 1], pos, 2)
				index += 1
		pygame.display.update()

	save_path_plan(path_wp)
