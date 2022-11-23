from abc import ABC, abstractmethod

import numpy as np
import pygame

from settings import GameSettings


class Entity(ABC):
    def __init__(self, game_settings: GameSettings, pos=np.array([0, 0]),
                 colour=(255, 0, 0), **kwargs):

        self._pos = pos
        self.colour = colour
        self.game_settings: GameSettings = game_settings

        self.kwargs = kwargs

    @abstractmethod
    def draw(self, win):
        pass

    @abstractmethod
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


class CharacterEntity(Entity):
    def __init__(self, *args, width=5, v=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.v = v

    def draw(self, win):
        pygame.draw.circle(win, self.colour, (int(self.pos[0]), int(self.pos[1])), self.width)


class fObjeto(Entity, ABC):

    @property
    @abstractmethod
    def v(self):
        pass

    @property
    @abstractmethod
    def a(self):
        pass

    @property
    @abstractmethod
    def pos(self):
        pass

    def distance_to(self, other):
        return np.linalg.norm(self.pos - other.pos)