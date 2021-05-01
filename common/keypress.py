import pygame


def init():
	pygame.init()
	win = pygame.display.set_mode((400, 400))


def kp_init():
	init()


def is_key_pressed(keyName):
	ans = False
	for eve in pygame.event.get(): pass
	keyInput = pygame.key.get_pressed()
	myKey = getattr(pygame, 'K_{}'.format(keyName))

	if keyInput[myKey]:
		ans = True

	pygame.display.update()
	return ans


def main():
	if is_key_pressed("LEFT"):
		print("Left key pressed")

	if is_key_pressed("RIGHT"):
		print("Right key Pressed")


if __name__ == '__main__':
	init()
	while True:
		main()
