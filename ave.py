import random
from typing import List
import numpy as np
import pygame
import config

random.seed(20)



class Bandada:
    def __init__(self):
        self._aves: List[Ave] = None

    def generarAves(self, numAves, radioLocal=10, velMax=10):
        self._aves = [
            Ave(
                pos=np.array([random.randint(0, config.mapWidth),
                              random.randint(0, config.mapHeight)]),
                bandada=self,
                radioLocal=radioLocal,
                velMax=velMax
            )
            for _ in range(numAves) # que es esto?......
        ]

    @property
    def aves(self):
        return self._aves

    def getAvesCercanas(self, ave):
        return [otraAve for otraAve in self.aves
                if ave.calcDistancia(otraAve) < ave.radioLocal and ave != otraAve]


class Ave():
    def __init__(self, bandada: Bandada, pos=np.array([0, 0]), color=config.colorAves, size=10, radioLocal=200, velMax=30,
                 velocidad=20):
        self._pos = pos
        self.color = color
        self.bandada = bandada
        self.size = size
        self.radioLocal = radioLocal
        self.velMax = velMax
        self.velocidad = velocidad
        self._vel = np.array([0, 0])
        self.numVecinos = 0

    def bordePeriodico(self):
        if self.pos[0] > config.mapWidth:
            self.pos[0]=0
        if self.pos[0] < 0:
            self.pos[0]=config.mapWidth
        if self.pos[1] > config.mapHeight:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=config.mapHeight

    def actualizar(self, ventana, tiempoTranscurrido):
        self.actualizarVelPos(tiempoTranscurrido)
        self.bordePeriodico()
        self.draw(ventana)
    
    def calcDistancia(self, other):
        return calcDistanciaPeriodica(self.pos, other.pos)

    @property
    def pos(self):
        return self._pos

    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, vel):
        magnitud = np.linalg.norm(vel)
        if magnitud > self.velMax:
            vel = vel * (self.velMax/magnitud)
        self._vel = vel

    def draw(self, ventana):
        if abs(self.vel).sum() == 0:
            dir = np.array([0, 1])
        else:
            dir = self.vel / np.linalg.norm(self.vel)

        dir *= self.size
        dirPerpendicular = np.cross(np.array([*dir, 0]), np.array([0, 0, 1]))[:2] # que es np.cross?

        centro = self.pos

        points = [
            0.1*dir + centro,
            -0.75*dir + 0.8*dirPerpendicular + centro,
            -0.75*dir - 0.8*dirPerpendicular + centro,
        ] # entender mejor como funciona esto

        pygame.draw.polygon(ventana, self.color, points)

    def actualizarVelPos(self, tiempoTranscurrido):

        avesCercanas: List[Ave] = self.bandada.getAvesCercanas(self)

        dir = self.calcularReglas(avesCercanas)
        self.numVecinos = len(avesCercanas)

        self.vel = self.vel + dir * self.velocidad

        self._pos += (self.vel * tiempoTranscurrido).astype(int)

    def calcularReglas(self, avesCercanas):
        # Se obtiene un "promedio ponderado" de direccion resultante tras consultar todas las reglas
        regla1 = ReglaSeparacion(ponderacion=config.pesoSeparacion, fuerzaEmpuje=config.areaAlejamiento, ave = self, avesCercanas=avesCercanas)
        regla2 = ReglaAlineamiento(ponderacion=config.pesoAlineamiento, avesCercanas=avesCercanas)
        regla3 = ReglaCohesion(ponderacion=config.pesoCohesion, ave=self, avesCercanas=avesCercanas)
        regla4 = MovAleatorio(ponderacion=config.pesoMovAleatorio)
        return sum([regla1,regla2,regla3,regla4])


def ReglaSeparacion(ponderacion, fuerzaEmpuje, ave, avesCercanas):
    n = len(avesCercanas)
    if n > 1:
        # Vectores de diferencia apuntan en la dirección contraria a cada vecino, desde la perspectiva del ave actual
        difPosiciones = np.array([calcDistEjePeriodica(ave.pos,otraAve.pos) for otraAve in avesCercanas])
        magnitudes = np.array([ave.calcDistancia(otraAve) for otraAve in avesCercanas])
        # Obtener vectores unitarios que apuntan en la direccion contraria a cada vecino
        dirNormalizadas = difPosiciones / magnitudes[:, np.newaxis] # Trasponer el vector de magnitudes (para que quede como vector columna)
        # Obtener un vector
        vel = np.sum(dirNormalizadas * (fuerzaEmpuje/magnitudes)[:, np.newaxis], axis=0)
    else:
        vel = np.array([0, 0])
    return vel * ponderacion


def ReglaAlineamiento(ponderacion, avesCercanas):
    if len(avesCercanas)< 1:
        return np.array([0,0])
    # Obtener los vectores de velocidad de las aves cercanas
    velocidades = np.array([b.vel for b in avesCercanas])
    if len(velocidades) < 1:
        return np.array([0, 0])
    # Obtener las magnitudes de cada vector
    magnitudes = np.sum(np.abs(velocidades) ** 2, axis=-1) ** (1. / 2)
    magnitudes[magnitudes==0] = 0.00001
    # Obtener vectores de velocidad normalizados
    velNormalizadas: np.ndarray = velocidades / magnitudes[:, np.newaxis]
    # Promedio de las direcciones de las aves cercanas, sin contar su magnitud, solo su direccion
    vel: np.ndarray = velNormalizadas.mean(axis=0)
    return vel * ponderacion


def ReglaCohesion(ponderacion, ave, avesCercanas):
    if len(avesCercanas) == 0:
        return np.array([0, 0])
    # "Centro de gravedad" de las aves cercanas:
    posPromedio = np.array([b.pos for b in avesCercanas]).mean(axis=0)
    diff = calcDistEjePeriodica(posPromedio, ave.pos)
    #diff = posPromedio - ave.pos
    mag = np.sqrt((diff**2).sum())
    if mag == 0:
        return np.array([0, 0])
    return ponderacion * diff / mag


def MovAleatorio(ponderacion):
    return np.random.uniform(-1, 1, 2)*ponderacion


def calcDistanciaPeriodica(P1, P2):
    distX = abs(P1[0] - P2[0])
    distY = abs(P1[1] - P2[1])
    if distX > config.mapWidth/2:
        distX = config.mapWidth - distX
    if distY > config.mapHeight/2:
        distY = config.mapHeight - distY
    dist = (distX**2+distY**2)**(0.5)
    if dist == 0.0:
        dist = 0.0000001
    return dist

def calcDistEjePeriodica(P1, P2):
    # Obtener un vector que apunta desde P2 a P1
    distX = P1[0] - P2[0]
    distY = P1[1] - P2[1]
    if abs(distX) > config.mapWidth/2:
        distX = config.mapWidth - distX
    if abs(distY) > config.mapHeight/2:
        distY = config.mapHeight - distY
    return np.array([distX, distY])