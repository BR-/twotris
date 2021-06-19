import sys, pygame
pygame.init()

def xyxy2rect(x1, y1, x2, y2):
	return pygame.Rect(x1, y1, x2-x1, y2-y1)

size = width, height = 1280, 1024
speed = [1, 1]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.png").convert()
ballrect = ball.get_rect()

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

	ballrect = ballrect.move(speed)
	if ballrect.left < 0 or ballrect.right > width:
		speed[0] = -speed[0]
	if ballrect.top < 0 or ballrect.bottom > height:
		speed[1] = -speed[1]

	screen.fill(black)
	screen.blit(ball, ballrect)
	pygame.draw.rect(screen, white, xyxy2rect(345, 80, 830, 953), 3)
	pygame.draw.rect(screen, white, xyxy2rect(907, 58, 1041, 197), 3)
	pygame.draw.rect(screen, white, xyxy2rect(907, 197, 1041, 921), 3)
	pygame.draw.rect(screen, white, xyxy2rect(200, 98, 309, 230), 3)
	pygame.display.flip()