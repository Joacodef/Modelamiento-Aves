import numpy as np

class GameSettings:
    def __init__(self):
        self.window_width = 1000
        self.window_height = 900

        self.map_width = 1000
        self.map_height = 900

        self.camera_pos = np.array([0, 0])
        self.zoom = 1
        self.zoom_factor = 0.05

        self.is_running = True
        self.ticks_per_second = 144