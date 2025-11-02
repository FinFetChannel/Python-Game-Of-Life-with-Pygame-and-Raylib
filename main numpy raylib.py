import pyray as rl
import numpy as np
import random

class Simulation:
    def __init__(self, width, height, cell_size):
        self.rows = height // cell_size
        self.cols = width // cell_size
        self.cell_size = cell_size
        self.grid = np.zeros((self.rows, self.cols), dtype=np.uint8)
        self.run = False
        self.dirty = True

    def randomize(self):
        if not self.run:
            self.grid = np.random.choice([0, 1], size=(self.rows, self.cols), p=[0.75, 0.25]).astype(np.uint8)
            self.dirty = True

    def clear(self):
        if not self.run:
            self.grid.fill(0)
            self.dirty = True

    def toggle_cell(self, r, c):
        if not self.run and 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r, c] ^= 1
            self.dirty = True

    def update(self):
        if not self.run:
            return False

        # Use convolution-like neighbor counting with NumPy roll
        neighbors = sum(
            np.roll(np.roll(self.grid, dr, axis=0), dc, axis=1)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if not (dr == 0 and dc == 0)
        )

        self.grid = ((neighbors == 3) | ((self.grid == 1) & (neighbors == 2))).astype(np.uint8)


# --- MAIN ---
WIDTH, HEIGHT, CELL = 1000, 1000, 8
FPS = 20

rl.init_window(WIDTH, HEIGHT, b"Game of Life Raylib (NumPy)")
#rl.set_target_fps(FPS)

sim = Simulation(WIDTH, HEIGHT, CELL)
grid_tex = rl.load_render_texture(WIDTH, HEIGHT)

def redraw_texture():
    rl.begin_texture_mode(grid_tex)
    rl.clear_background(rl.Color(29, 29, 29, 255))
    for r in range(sim.rows):
        for c in range(sim.cols):
            color = (0, 255, 0, 255) if sim.grid[r][c] else  (55, 55, 55, 255)
            rl.draw_rectangle(c * CELL, r * CELL, CELL - 1, CELL - 1, color)

    rl.end_texture_mode()
    sim.dirty = False

while not rl.window_should_close():
    # Input
    if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
        x, y = rl.get_mouse_x(), rl.get_mouse_y()
        sim.toggle_cell(y // CELL, x // CELL)

    if rl.is_key_pressed(rl.KEY_ENTER):
        sim.run = True
        rl.set_window_title(b"Running")
    if rl.is_key_pressed(rl.KEY_SPACE):
        sim.run = False
        rl.set_window_title(b"Stopped")
    if rl.is_key_pressed(rl.KEY_R):
        sim.randomize()
    if rl.is_key_pressed(rl.KEY_C):
        sim.clear()

    # Update
    sim.update()
    redraw_texture()

    # Draw
    rl.begin_drawing()
    rl.clear_background((29,29,29,255))
    rl.draw_texture_rec(
        grid_tex.texture,
        rl.Rectangle(0, 0, grid_tex.texture.width, -grid_tex.texture.height),
        rl.Vector2(0, 0),
        rl.WHITE,
    )
    rl.draw_text(f"{int(rl.get_fps())}".encode(), 15, 15, 20, rl.WHITE)
    rl.end_drawing()

rl.unload_render_texture(grid_tex)
rl.close_window()
