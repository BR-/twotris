import random

class Mino:
	def __init__(self, name, shape):
		self.name = name
		self.shape = shape
		self.reset()

	def __str__(self):
		return f"Mino<{self.name}, ({self.x, self.y})@{self.rotation}>"

	def reset(self):
		self.x = 0
		self.y = 0
		self.rotation = 0
		minx = min(sq[0] for sq in self.shape)
		if minx < 0:
			self.x = -1 * minx
		miny = min(sq[1] for sq in self.shape)
		if miny < 0:
			self.y = -1 * miny

	def clone(self):
		m = Mino(self.name, self.shape)
		m.x = self.x
		m.y = self.y
		m.rotation = self.rotation
		return m

	def rotate_cw(self):
		self.rotation = (self.rotation - 1) % 4

	def rotate_ccw(self):
		self.rotation = (self.rotation + 1) % 4

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def get(self):
		for square in self.shape:
			x,y = square
			for r in range(self.rotation):
				x,y = y,-x
			x += self.x
			y += self.y
			yield (x, y)

	minos = {
		"I": [
			(-2, 0),
			(-1, 0),
			(0, 0),
			(1, 0),
		],
		"J": [
			(-1, -1),
			(-1, 0),
			(0, 0),
			(1, 0),
		],
		"L": [
			(-1, 0),
			(0, 0),
			(1, 0),
			(1, -1),
		],
		"O": [
			(-1, -1),
			(-1, 0),
			(0, 0),
			(0, -1),
		],
		"S": [
			(-1, 0),
			(0, 0),
			(0, -1),
			(1, -1),
		],
		"Z": [
			(1, 0),
			(0, 0),
			(0, -1),
			(-1, -1),
		],
		"T": [
			(0, 0),
			(1, 0),
			(-1, 0),
			(0, -1),
		]
	}

def bag_rng():
	bag = list(Mino.minos.keys())
	while True:
		random.shuffle(bag)
		for mino in bag:
			yield Mino(mino, Mino.minos[mino])

class Tetris:
	def __init__(self):
		self.board = [[0] * 20 for _ in range(10)]

		self.piece_generator = bag_rng()
		self.piece_queue = [next(self.piece_generator) for _ in range(7)]
		self.drop_new_piece_in()

		self.hold = None
		self.hold_available = False

		self.game_over = False

	def drop_new_piece_in(self, piece=None):
		if piece is None:
			piece = self.piece_queue.pop(0)
			self.piece_queue.append(next(self.piece_generator))
		piece.reset()
		self.dropping_mino = piece
		self.dropping_mino.move(4, 0)
		if self.check_collision():
			self.game_over = True

	def attempt_hold(self):
		if self.game_over:
			return
		if not self.hold_available:
			return
		self.dropping_mino.reset()
		held = self.hold
		self.hold = self.dropping_mino
		self.hold_available = False
		self.drop_new_piece_in(held)

	def lock_in(self):
		self.hold_available = True
		for x,y in self.dropping_mino.get():
			self.board[x][y] += 1
		for y in range(20):
			good = True
			for x in range(10):
				if self.board[x][y] != 2:
					good = False
					break
			if good:
				for y2 in range(y-1, -1, -1):
					for x in range(10):
						self.board[x][y2+1] = self.board[x][y2]
		self.drop_new_piece_in()

	def attempt_action(self, action, lock_if_fail=False):
		if self.game_over:
			return
		backup = self.dropping_mino.clone()
		action(self.dropping_mino)
		if self.check_collision():
			self.dropping_mino = backup
			if lock_if_fail:
				self.lock_in()

	def hard_drop(self):
		if self.game_over:
			return
		while True:
			backup = self.dropping_mino.clone()
			self.dropping_mino.move(0, 1)
			if self.check_collision():
				self.dropping_mino = backup
				self.lock_in()
				return

	def check_collision(self):
		for x,y in self.dropping_mino.get():
			if x < 0 or x >= 10 or y >= 20:
				return True
			elif y < 0:
				continue
			elif self.board[x][y] == 2:
				return True
		return False

import sys, pygame
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont("Comic Sans MS", 30)

def xyxy2rect(x1, y1, x2, y2):
	return pygame.Rect(x1, y1, x2-x1, y2-y1)

size = width, height = 1280, 1024
speed = [1, 1]
black = 0, 0, 0
gray = 100, 100, 100
white = 255, 255, 255
red = 100, 0, 0

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Twotris")

ball = pygame.image.load("ball.png").convert()
ballrect = ball.get_rect()

tetris = Tetris()
last_piece_drop = 0
paused = False

while 1:
	ballrect = ballrect.move(speed)
	if ballrect.left < 0 or ballrect.right > width:
		speed[0] = -speed[0]
	if ballrect.top < 0 or ballrect.bottom > height:
		speed[1] = -speed[1]

	if tetris.game_over:
		screen.fill(red)
	else:
		screen.fill(black)
	screen.blit(ball, ballrect)
	# HELD PIECE
	if tetris.hold is not None:
		color = [gray, white][tetris.hold_available]
		for x,y in tetris.hold.get():
			w = (309 - 200) / 4
			h = (230 - 98) / 4
			xx = 200 + w * x
			yy = 98 + h * y
			pygame.draw.rect(screen, color, (xx, yy, w, h))
	# NEXT PIECE
	for x,y in tetris.piece_queue[0].get():
		w = (1041 - 907) / 4
		h = (197 - 58) / 4
		xx = 907 + w * x
		yy = 58 + h * y
		pygame.draw.rect(screen, white, (xx, yy, w, h))
	# NEXT QUEUE
	for ndx, piece in enumerate(tetris.piece_queue[1:]):
		for x,y in piece.get():
			w = (1041 - 907) / 4
			h = (921 - 197) / 4 / 6
			xx = 907 + w * x
			yy = 197 + h * (y + 4 * ndx)
			pygame.draw.rect(screen, gray, (xx, yy, w, h))
	# EXISTING GAME BOARD
	for x in range(10):
		for y in range(20):
			w = (830 - 345) / 10
			h = (953 - 80) / 20
			xx = 345 + w * x
			yy = 80 + h * y
			color = [False, gray, white][tetris.board[x][y]]
			if color:
				pygame.draw.rect(screen, color, (xx, yy, w, h))
	# DROPPING PIECE
	for x,y in tetris.dropping_mino.get():
		w = (830 - 345) / 10
		h = (953 - 80) / 20
		xx = 345 + w * x
		yy = 80 + h * y
		if y < 0:
			color = False
		else:
			color = [False, gray, white][tetris.board[x][y] + 1]
		if color:
			pygame.draw.rect(screen, color, (xx, yy, w, h))
	# BOARD GRID
	minx = min(sq[0] for sq in tetris.dropping_mino.get())
	maxx = max(sq[0] for sq in tetris.dropping_mino.get())
	for x in range(1, 10):
			xx = 345 + (830 - 345) * x / 10
			color = gray
			if x == minx or x == maxx+1:
				color = white
			pygame.draw.line(screen, color, (xx, 80), (xx, 953))
	for y in range(1, 20):
			yy = 80 + (953 - 80) * y / 20
			pygame.draw.line(screen, gray, (345, yy), (830, yy))
	# UI BORDERS
	pygame.draw.rect(screen, white, xyxy2rect(345, 80, 830, 953), 3) # BOARD
	pygame.draw.rect(screen, white, xyxy2rect(907, 58, 1041, 197), 3) # NEXT
	pygame.draw.rect(screen, white, xyxy2rect(907, 197, 1041, 921), 3) # NEXT QUEUE
	pygame.draw.rect(screen, white, xyxy2rect(200, 98, 309, 230), 3) # HOLD
	pygame.display.flip()
	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			sys.exit()
		elif ev.type == pygame.KEYDOWN:
			if ev.key == pygame.K_ESCAPE:
				sys.exit()
			elif ev.key == pygame.K_F1:
				paused = not paused
			elif ev.key == pygame.K_LEFT:
				tetris.attempt_action(lambda x: x.move(-1, 0))
			elif ev.key == pygame.K_RIGHT:
				tetris.attempt_action(lambda x: x.move(1, 0))
			elif ev.key == pygame.K_DOWN:
				tetris.attempt_action(lambda x: x.move(0, 1), True)
			elif ev.key == pygame.K_UP or ev.key == pygame.K_x:
				tetris.attempt_action(lambda x: x.rotate_cw())
			elif ev.key == pygame.K_z or ev.key == pygame.K_LCTRL:
				tetris.attempt_action(lambda x: x.rotate_ccw())
			elif ev.key == pygame.K_SPACE:
				tetris.hard_drop()
			elif ev.key == pygame.K_LSHIFT or ev.key == pygame.K_c:
				tetris.attempt_hold()
	ticks = pygame.time.get_ticks()
	if not paused and ticks > last_piece_drop + 200:
		tetris.attempt_action(lambda x: x.move(0, 1), True)
		last_piece_drop = ticks
