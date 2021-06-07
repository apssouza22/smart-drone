import math


def get_distance(pos0, pos1):
	"""
	Get distance between 2 position.
	"""
	x = abs(pos0[0] - pos1[0])
	y = abs(pos0[1] - pos1[1])
	return math.hypot(x, y)
