import random
from typing import List
import numpy as np
import pygame
import config

class Bandada:
    def __init__(self):
        self._aves: List[Ave] = None

    def generarAves(self, numAves, reglas=None, radioLocal=10, velMax=10):
        self._aves = [
            Ave(
                pos=np.array([random.randint(0, config.mapWidth),
                              random.randint(0, config.mapHeight)]),
                reglas=reglas,
                bandada=self,
                radioLocal=radioLocal,
                velMax=velMax
            )
            for _ in range(numAves)
        ]

    @property
    def aves(self):
        return self._aves

    def get_local_aves(self, ave):
        return [otraAve for otraAve in self.aves
                if ave.calcDistancia(otraAve) < ave.radioLocal and ave != otraAve]


class Ave():
    def __init__(self, pos=np.array([0, 0]), *args, bandada: Bandada, colour=config.colorAves, reglas=None, size=10, radioLocal=200, velMax=30,
                 velocidad=20):

        if reglas is None:
            reglas = list()

        self._pos = pos
        self.colour = colour
        self.bandada = bandada
        self.size = size

        self.radioLocal = radioLocal
        self.velMax = velMax
        self.velocidad = velocidad
        self._v = np.array([0, 0])

        self.reglas = reglas
        self.n_neighbours = 0

    def bordePeriodico(self):
        if self.pos[0] > config.mapWidth:
            self.pos[0]=0
        if self.pos[0] < 0:
            self.pos[0]=config.mapWidth
        if self.pos[1] > config.mapHeight:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=config.mapHeight

    def actualizar(self, win, tiempoTranscurrido):
        self.actualizarVelPos(tiempoTranscurrido)
        self.bordePeriodico()
        self.draw(win)
    
    def calcDistancia(self, other):
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
        if magnitude > self.velMax:
            v = v * (self.velMax/magnitude)
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

    def actualizarVelPos(self, tiempoTranscurrido):

        local_aves: List[Ave] = self.bandada.get_local_aves(self)

        direction = self.calculate_reglas(local_aves)
        self.n_neighbours = len(local_aves)

        self.v = self.v + direction * self.velocidad

        self._pos += (self.v * tiempoTranscurrido).astype(int)

    def calculate_reglas(self, local_aves):
        #por cada regla, 
        return sum(
            [rule.evaluate(self, local_aves) * rule.peso for rule in self.reglas]
        )


class Regla():
    def __init__(self, ponderacion: float):
        self._peso = ponderacion

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
    def peso(self):
        return self._peso

    @peso.setter
    def peso(self, value):
        self._peso = value


class ReglaSeparacion(Regla):
    def __init__(self, ponderacion, push_force=5):
        super().__init__(ponderacion)
        self.push_force = push_force

    def _evaluate(self, ave: Ave, local_aves: List[Ave]):
        n = len(local_aves)
        if n > 1:
            direction_offsets = np.array([(ave.pos - otraAve.pos) for otraAve in local_aves])
            magnitudes = np.sum(np.abs(direction_offsets)**2, axis=-1)**(1./2)
            normed_directions = direction_offsets / magnitudes[:, np.newaxis]
            v = np.sum(normed_directions * (self.push_force/magnitudes)[:, np.newaxis], axis=0)
        else:
            v = np.array([0, 0])

        return v


class ReglaAlineamiento(Regla):
    def __init__(self, ponderacion):
        super().__init__(ponderacion)

    def _evaluate(self, ave: Ave, local_aves):
        other_velocities = np.array([b.v for b in local_aves])

        if len(other_velocities) == 0:
            return np.array([0, 0])

        magnitudes = np.sum(np.abs(other_velocities) ** 2, axis=-1) ** (1. / 2)
        normed_directions: np.ndarray = other_velocities / magnitudes[:, np.newaxis]

        v: np.ndarray = normed_directions.mean(axis=0)
        return v


class ReglaCohesion(Regla):
    def __init__(self, ponderacion):
        super().__init__(ponderacion)

    def _evaluate(self, ave: Ave, local_aves: List[Ave]):
        if len(local_aves) == 0:
            return np.array([0, 0])
        # "Centro de gravedad" de las aves cercanas:
        average_pos = np.array([b.pos for b in local_aves]).mean(axis=0)
        diff = average_pos - ave.pos
        mag = np.sqrt((diff**2).sum())
        if mag == 0:
            return np.array([0, 0])
        return diff / mag


class MovAleatorio(Regla):
    def __init__(self, ponderacion):
        super().__init__(ponderacion)

    def _evaluate(self, ave, local_aves: List[Ave]):
        return np.random.uniform(-1, 1, 2)