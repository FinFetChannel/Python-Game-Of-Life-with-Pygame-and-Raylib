import pygame, sys
import random

class Grid:
	def __init__(self, width, height, cell_size):
		self.rows = height // cell_size
		self.columns = width // cell_size
		self.cell_size = cell_size
		self.cells = [[0 for _ in range(self.columns)] for _ in range(self.rows)]

	def draw(self, window):
		for row in range(self.rows):
			for column in range(self.columns):
				color = (0, 255, 0) if self.cells[row][column] else  (55, 55, 55)
				pygame.draw.rect(window, color, (column * self.cell_size, row * self.cell_size, self.cell_size -1, self.cell_size - 1))

	def fill_random(self):
		for row in range(self.rows):
			for column in range(self.columns):
				self.cells[row][column] = random.choice([1, 0, 0, 0])

	def clear(self):
		for row in range(self.rows):
			for column in range(self.columns):
				self.cells[row][column] = 0

	def toggle_cell(self, row, column):
		if 0 <= row < self.rows and 0 <= column < self.columns:
			self.cells[row][column] = not self.cells[row][column]

class Simulation:
	def __init__(self, width, height, cell_size):
		self.grid = Grid(width, height, cell_size)
		self.temp_grid = Grid(width, height, cell_size)
		self.rows = height // cell_size
		self.columns = width // cell_size
		self.run = False

	def draw(self, window):
		self.grid.draw(window)

	def count_live_neighbors(self, grid, row, column):
		live_neighbors = 0

		neighbor_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
		for offset in neighbor_offsets:
			new_row = (row + offset[0]) % self.rows
			new_column = (column + offset[1]) % self.columns
			if self.grid.cells[new_row][new_column] == 1:
				live_neighbors += 1

		return live_neighbors

	def update(self):
		if self.is_running():
			for row in range(self.rows):
				for column in range(self.columns):
					live_neighbors = self.count_live_neighbors(self.grid, row, column)
					cell_value = self.grid.cells[row][column]

					if cell_value == 1:
						if live_neighbors > 3 or live_neighbors < 2:
							self.temp_grid.cells[row][column] = 0
						else:
							self.temp_grid.cells[row][column] = 1
					else:
						if live_neighbors == 3:
							self.temp_grid.cells[row][column] = 1
						else:
							self.temp_grid.cells[row][column] = 0

			for row in range(self.rows):
				for column in range(self.columns):
					self.grid.cells[row][column] = self.temp_grid.cells[row][column]

	def is_running(self):
		return self.run

	def start(self):
		self.run = True

	def stop(self):
		self.run = False

	def clear(self):
		if self.is_running() == False:
			self.grid.clear()

	def create_random_state(self):
		if self.is_running() == False:
			self.grid.fill_random()

	def toggle_cell(self, row, column):
		if self.is_running() == False:
			self.grid.toggle_cell(row, column)

pygame.init()

GREY = (29, 29, 29)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
CELL_SIZE = 8
FPS = 12

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Game of Life")

clock = pygame.time.Clock()
simulation = Simulation(WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE)

font = pygame.font.Font()

#Simulation Loop
while True:

	# 1. Event Handling
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			row = pos[1] // CELL_SIZE
			column = pos[0] // CELL_SIZE
			simulation.toggle_cell(row, column)
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				simulation.start()
				pygame.display.set_caption("Game of Life is running")
			elif event.key == pygame.K_SPACE:
				simulation.stop()
				pygame.display.set_caption("Game of Life has stopped")
			elif event.key == pygame.K_f:
				FPS += 2
			elif event.key == pygame.K_s:
				if FPS > 5:
					FPS -= 2
			elif event.key == pygame.K_r:
				simulation.create_random_state()
			elif event.key == pygame.K_c:
				simulation.clear()

	# 2. Updating State
	simulation.update()

	# 3. Drawing
	window.fill(GREY)
	simulation.draw(window)
	fps = int(clock.get_fps())
	fps_text = font.render(str(fps), 1, (255,255,255))
	window.blit(fps_text, (15,15))

	pygame.display.update()
	clock.tick()