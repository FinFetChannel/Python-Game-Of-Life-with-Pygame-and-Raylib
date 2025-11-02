import pyray as rl
import random

class Grid:
    def __init__(self, width, height, cell_size):
        self.rows = height // cell_size
        self.cols = width // cell_size
        self.cell_size = cell_size
        self.cells = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def fill_random(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c] = random.choice([1, 0, 0, 0])

    def clear(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c] = 0

    def toggle_cell(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.cells[r][c] = 0 if self.cells[r][c] else 1


class Simulation:
    def __init__(self, width, height, cell_size):
        self.grid = Grid(width, height, cell_size)
        self.temp = Grid(width, height, cell_size)
        self.rows = height // cell_size
        self.cols = width // cell_size
        self.cell_size = cell_size
        self.run = False
        self.dirty = True  # controls when texture redraw needed

    def count_live_neighbors(self, r, c):
        offsets = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        count = 0
        for dr, dc in offsets:
            rr = (r + dr) % self.rows
            cc = (c + dc) % self.cols
            count += self.grid.cells[rr][cc]
        return count

    def update(self):
        if not self.run:
            return False
        for r in range(self.rows):
            for c in range(self.cols):
                live = self.count_live_neighbors(r, c)
                val = self.grid.cells[r][c]
                if val == 1:
                    self.temp.cells[r][c] = 1 if 2 <= live <= 3 else 0
                else:
                    self.temp.cells[r][c] = 1 if live == 3 else 0
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid.cells[r][c] = self.temp.cells[r][c]
        self.dirty = True
        return True

    def start(self): self.run = True
    def stop(self): self.run = False
    def clear(self):
        if not self.run:
            self.grid.clear()
            self.dirty = True
    def randomize(self):
        if not self.run:
            self.grid.fill_random()
            self.dirty = True
    def toggle_cell(self, r, c):
        if not self.run:
            self.grid.toggle_cell(r, c)
            self.dirty = True

# --- MAIN ---
WIDTH, HEIGHT, CELL = 1000, 1000, 8
FPS = 60

rl.init_window(WIDTH, HEIGHT, b"Game of Life Raylib")
#rl.set_target_fps(FPS)

sim = Simulation(WIDTH, HEIGHT, CELL)

# Create render texture to store grid image
grid_tex = rl.load_render_texture(WIDTH, HEIGHT)

def redraw_texture():
    rl.begin_texture_mode(grid_tex)
    for r in range(sim.rows):
        for c in range(sim.cols):
            color = (0, 255, 0, 255) if sim.grid.cells[r][c] else  (55, 55, 55, 255)
            rl.draw_rectangle(c * CELL, r * CELL, CELL - 1, CELL - 1, color)

    rl.end_texture_mode()
    sim.dirty = False

while not rl.window_should_close():
    # Input
    if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
        x, y = rl.get_mouse_x(), rl.get_mouse_y()
        sim.toggle_cell(y // CELL, x // CELL)
    if rl.is_key_pressed(rl.KEY_ENTER):
        sim.start()
        rl.set_window_title(b"Running")
    if rl.is_key_pressed(rl.KEY_SPACE):
        sim.stop()
        rl.set_window_title(b"Stopped")
    if rl.is_key_pressed(rl.KEY_R):
        sim.randomize()
    if rl.is_key_pressed(rl.KEY_C):
        sim.clear()
    if rl.is_key_pressed(rl.KEY_F):
        FPS += 2
        rl.set_target_fps(FPS)
    if rl.is_key_pressed(rl.KEY_S) and FPS > 5:
        FPS -= 2
        rl.set_target_fps(FPS)

    # Update
    if sim.update() or sim.dirty:
        redraw_texture()

    # Draw
    rl.begin_drawing()
    rl.clear_background((29,29,29,255))
    rl.draw_texture_rec(grid_tex.texture,
                        rl.Rectangle(0, 0, grid_tex.texture.width, -grid_tex.texture.height),
                        rl.Vector2(0, 0),
                        rl.WHITE)
    rl.draw_text(f"{int(rl.get_fps())}".encode(), 15, 15, 20, rl.WHITE)
    rl.end_drawing()

rl.unload_render_texture(grid_tex)
rl.close_window()
