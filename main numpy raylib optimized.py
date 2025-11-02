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

rl.init_window(WIDTH, HEIGHT, b"Game of Life Raylib (NumPy Optimized)")
#rl.set_target_fps(FPS)

sim = Simulation(WIDTH, HEIGHT, CELL)
grid_tex = rl.load_render_texture(sim.cols, sim.rows)

def redraw_texture():
    rl.begin_texture_mode(grid_tex)
    rl.clear_background((55, 55, 55, 255))
    for r in range(sim.rows):
        for c in range(sim.cols):
            if sim.grid[r][c]:
                rl.draw_pixel(c, r, rl.GREEN)
    rl.end_texture_mode()

rgba = np.zeros((sim.rows, sim.cols, 4), dtype=np.uint8)

def redraw_texture_fast():
    # Create RGBA image from grid
    
    rgba[sim.grid == 1] = [0, 255, 0, 255]      # live cells
    rgba[sim.grid == 0] = [55, 55, 55, 255]     # dead cells

    # Upload to texture (single GPU call)
    c_buffer = rl.ffi.cast("unsigned char *", np.ascontiguousarray(rgba, dtype=np.uint8).ctypes.data)
    rl.update_texture(grid_tex.texture, c_buffer)

def create_gridlines_texture(width, height, cell_size):
    tex = rl.load_render_texture(width, height)
    rl.begin_texture_mode(tex)
    rl.clear_background(rl.BLANK)  # fully transparent

    line_color = rl.Color(29, 29, 29, 255)
    for x in range(0, width, cell_size):
        rl.draw_line(x, 0, x, height, line_color)
    for y in range(0, height, cell_size):
        rl.draw_line(0, y, width, y, line_color)

    rl.end_texture_mode()
    return tex

gridlines_tex = create_gridlines_texture(WIDTH, HEIGHT, CELL)

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
    #redraw_texture()
    redraw_texture_fast()

    # Draw
    rl.begin_drawing()
    rl.draw_texture_pro(grid_tex.texture, rl.Rectangle(0, 0, grid_tex.texture.width, -grid_tex.texture.height),
                        rl.Rectangle(0, 0, WIDTH, HEIGHT), rl.Vector2(0, 0), 0, rl.WHITE)
    rl.draw_texture(gridlines_tex.texture, 0, 0, rl.WHITE)

    rl.draw_text(f"{int(rl.get_fps())}".encode(), 15, 15, 20, rl.WHITE)
    rl.end_drawing()

rl.unload_render_texture(grid_tex)
rl.close_window()
