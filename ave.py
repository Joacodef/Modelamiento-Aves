import random
from typing import List
import numpy as np
import pygame
import config

class Bandada:
    def __init__(self):
        self._aves: List[Ave] = None

    def generate_aves(self, n_aves, rules=None, **kwargs):
        self._aves = [
            Ave(
                pos=np.array([random.randint(0, config.map_width),
                              random.randint(0, config.map_height)]),
                rules=rules,
                bandada=self,
                **kwargs,
            )
            for _ in range(n_aves)
        ]

    @property
    def aves(self):
        return self._aves

    def get_local_aves(self, ave):
        return [other_ave for other_ave in self.aves
                if ave.distance_to(other_ave) < ave.local_radius and ave != other_ave]


class Ave():
    def __init__(self, pos=np.array([0, 0]), *args, bandada: Bandada, colour=(0,0,0), rules=None, size=10, local_radius=200, max_velocity=30,
                 speed=20, **kwargs):

        if rules is None:
            rules = list()

        self._pos = pos
        self.colour = colour
        self.bandada = bandada
        self.size = size

        self.local_radius = local_radius
        self.max_velocity = max_velocity
        self.speed = speed
        self._v = np.array([0, 0])

        self.rules = rules
        self.n_neighbours = 0

    def check_physics(self):
        if self.pos[0] > config.map_width:
            self.pos[0]=0
        if self.pos[0] < 0:
            self.pos[0]=config.map_width
        if self.pos[1] > config.map_height:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=config.map_height

    def update(self, win, time_elapsed):
        self.update_physics(time_elapsed)
        self.check_physics()
        self.draw(win)
    
    def distance_to(self, other):
        return np.linalg.norm(self.pos - other.pos)
        
    def a(self):
        return 0

    @property
    def pos(self):
        return self._pos

    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, v):
        magnitude = np.linalg.norm(v)
        if magnitude > self.max_velocity:
            v = v * (self.max_velocity/magnitude)
        self._v = v

    def draw(self, win):
        if abs(self.v).sum() == 0:
            direction = np.array([0, 1])
        else:
            direction = self.v / np.linalg.norm(self.v)

        direction *= self.size
        perpendicular_direction = np.cross(np.array([*direction, 0]), np.array([0, 0, 1]))[:2]

        centre = self.pos

        points = [
            0.1*direction + centre,
            -0.75*direction + 0.8*perpendicular_direction + centre,
            -0.75*direction - 0.8*perpendicular_direction + centre,
        ]

        pygame.draw.polygon(win, self.colour, points)

    def update_physics(self, time_elapsed):

        local_aves: List[Ave] = self.bandada.get_local_aves(self)

        direction = self.calculate_rules(local_aves)
        self.n_neighbours = len(local_aves)

        self.v = self.v + direction * self.speed

        self._pos += (self.v * time_elapsed).astype(int)

    def calculate_rules(self, local_aves):
        return sum(
            [rule.evaluate(self, local_aves) * rule.weight for rule in self.rules]
        )


class AveRule():
    def __init__(self, weighting: float):
        self._weight = weighting

    def _evaluate(self, ave: Ave, local_aves: List[Ave]):
        pass

    def evaluate(self, ave, local_aves: List[Ave]):
        output = self._evaluate(ave, local_aves)
        if np.isnan(output).any():
            return np.array([0, 0])
        return output

    @property
    def name(self) -> str:
        return self._name

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value


class SimpleSeparationRule(AveRule):
    def __init__(self, *args, push_force=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_force = push_force

    def _evaluate(self, ave: Ave, local_aves: List[Ave], **kwargs):
        n = len(local_aves)
        if n > 1:
            direction_offsets = np.array([(ave.pos - other_ave.pos) for other_ave in local_aves])
            magnitudes = np.sum(np.abs(direction_offsets)**2, axis=-1)**(1./2)
            normed_directions = direction_offsets / magnitudes[:, np.newaxis]
            v = np.sum(normed_directions * (self.push_force/magnitudes)[:, np.newaxis], axis=0)
        else:
            v = np.array([0, 0])

        return v


class AlignmentRule(AveRule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _evaluate(self, ave: Ave, local_aves, **kwargs):
        other_velocities = np.array([b.v for b in local_aves])

        if len(other_velocities) == 0:
            return np.array([0, 0])

        magnitudes = np.sum(np.abs(other_velocities) ** 2, axis=-1) ** (1. / 2)
        normed_directions: np.ndarray = other_velocities / magnitudes[:, np.newaxis]

        v: np.ndarray = normed_directions.mean(axis=0)
        return v


class CohesionRule(AveRule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _evaluate(self, ave: Ave, local_aves: List[Ave], **kwargs):
        if len(local_aves) == 0:
            return np.array([0, 0])
        # "Centro de gravedad" de las aves cercanas:
        average_pos = np.array([b.pos for b in local_aves]).mean(axis=0)
        diff = average_pos - ave.pos
        mag = np.sqrt((diff**2).sum())
        if mag == 0:
            return np.array([0, 0])
        return diff / mag


class NoiseRule(AveRule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _evaluate(self, ave, local_aves: List[Ave], **kwargs):
        return np.random.uniform(-1, 1, 2)