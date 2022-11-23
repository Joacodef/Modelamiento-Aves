import numpy as np
from settings import GameSettings

class Entity():
    def __init__(self, game_settings: GameSettings, pos=np.array([0, 0]),
                 colour=(255, 0, 0), **kwargs):

        self._pos = pos
        self.colour = colour
        self.game_settings: GameSettings = game_settings

        self.kwargs = kwargs

    def draw(self, win):
        pass

    def update_physics(self,time_elapsed):
        pass

    def check_physics(self):
        if self.pos[0] > self.game_settings.map_width:
            self.pos[0]=0
        if self.pos[0] < 0:
            self.pos[0]=self.game_settings.map_width
        if self.pos[1] > self.game_settings.map_height:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=self.game_settings.map_height

    def update(self, win, time_elapsed):
        self.update_physics(time_elapsed)
        self.check_physics()
        self.draw(win)
    
    def distance_to(self, other):
        return np.linalg.norm(self.pos - other.pos)