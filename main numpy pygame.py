import pygame, sys, numpy as np, random

class Simulation:
    def __init__(self, width, height, cell_size):
        self.rows = height // cell_size
        self.cols = width // cell_size
        self.cell_size = cell_size
        self.grid = np.zeros((self.rows, self.cols), dtype=np.uint8)
        self.run = False
        self.img = np.zeros((self.rows, self.cols, 3), dtype=np.uint8)
        self.surf = pygame.surface.Surface((self.cols, self.rows))
        self.gridlines = pygame.surface.Surface((width, height))
        self.gridlines.set_colorkey((0,0,0))
        for x in range(0, width, cell_size):
            pygame.draw.line(self.gridlines, (55, 55, 55), (x, 0), (x, height), 1)
        for y in range(0, height, cell_size):
            pygame.draw.line(self.gridlines, (55, 55, 55), (0, y), (width, y), 1)

    def randomize(self):
        if not self.run:
            self.grid = np.random.choice([0, 1], size=(self.rows, self.cols), p=[0.75, 0.25]).astype(np.uint8)

    def clear(self):
        if not self.run:
            self.grid.fill(0)

    def toggle_cell(self, r, c):
        if not self.run and 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r, c] ^= 1

    def update(self):
        if not self.run:
            return
        neighbors = sum(
            np.roll(np.roll(self.grid, dr, axis=0), dc, axis=1)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if not (dr == 0 and dc == 0)
        )
        self.grid = ((neighbors == 3) | ((self.grid == 1) & (neighbors == 2))).astype(np.uint8)

    def draw(self, surface):
        self.img[self.grid == 1] = (0, 255, 0)
        self.img[self.grid == 0] = (29, 29, 29)

        pygame.surfarray.blit_array(self.surf, np.transpose(self.img, (1, 0, 2)))
        scaled = pygame.transform.scale(self.surf, surface.get_size())
        surface.blit(scaled, (0, 0))
        #surface.blit(self.gridlines, (0, 0))

# --- MAIN LOOP ---
pygame.init()
WIDTH, HEIGHT, CELL = 1000, 1000, 8
FPS = 12

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game of Life (NumPy + Gridlines)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
sim = Simulation(WIDTH, HEIGHT, CELL)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            sim.toggle_cell(y // CELL, x // CELL)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                sim.run = True
                pygame.display.set_caption("Running")
            elif event.key == pygame.K_SPACE:
                sim.run = False
                pygame.display.set_caption("Stopped")
            elif event.key == pygame.K_r:
                sim.randomize()
            elif event.key == pygame.K_c:
                sim.clear()
            elif event.key == pygame.K_f:
                FPS += 2
            elif event.key == pygame.K_s and FPS > 5:
                FPS -= 2

    sim.update()

    window.fill((29, 29, 29))
    sim.draw(window)
    fps_text = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
    window.blit(fps_text, (15, 15))

    pygame.display.update()
    clock.tick()
