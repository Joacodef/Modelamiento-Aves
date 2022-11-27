import random
from typing import List
import numpy as np
import pygame
import config
import threading
import time

#random.seed(20)

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

    def getvecinos(self, ave, grillaVecinos):
        listaVecinos = []
        posX = int(ave.pos[0]/config.radioDeteccion)
        posY = int(ave.pos[1]/config.radioDeteccion)
        dimXGrillaV = len(grillaVecinos[0])
        dimYGrillaV = len(grillaVecinos)
        #print("La pos del ave actual en la grilla vecinos es:", posX, posY)
        for i in [(posX-1)%dimXGrillaV,posX,(posX+1)%dimXGrillaV]:
            for j in [(posY-1)%dimYGrillaV,posY,(posY+1)%dimYGrillaV]:
                listaVecinos += grillaVecinos[i][j]
        #print(listaVecinos)
        return listaVecinos


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
            self.pos[0]=config.mapWidth + self.pos[0]
        if self.pos[1] > config.mapHeight:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=config.mapHeight + self.pos[1]

    def actualizar(self, ventana, tiempoTranscurrido, grillaVecinos):
        self.actualizarVelPos(tiempoTranscurrido, grillaVecinos)
        self.bordePeriodico()
        self.draw(ventana)
    
    def calcDistancia(self, other):
        return calcDistToro(self.pos, other.pos)

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
        dirPerpendicular = np.cross(np.array([*dir, 0]), np.array([0, 0, 1]))[:2] 

        centro = self.pos

        points = [
            0.1*dir + centro,
            -0.75*dir + 0.8*dirPerpendicular + centro,
            -0.75*dir - 0.8*dirPerpendicular + centro,
        ] 

        pygame.draw.polygon(ventana, self.color, points)

    def actualizarVelPos(self, tiempoTranscurrido, grillaVecinos):

        vecinos: List[Ave] = self.bandada.getvecinos(self, grillaVecinos)

        dir = self.calcularReglas(vecinos)
        self.numVecinos = len(vecinos)

        self.vel = self.vel + dir * self.velocidad

        self._pos += (self.vel * tiempoTranscurrido).astype(int)

    def calcularReglas(self, vecinos):
        # Se obtiene un "promedio ponderado" de direccion resultante tras consultar todas las reglas
        regla1 = ReglaSeparacion(ponderacion=config.pesoSeparacion, factorAlejamiento=config.factorAlejamiento, ave = self, vecinos=vecinos)
        regla2 = ReglaAlineamiento(ponderacion=config.pesoAlineamiento, vecinos=vecinos)
        regla3 = ReglaCohesion(ponderacion=config.pesoCohesion, ave=self, vecinos=vecinos)
        regla4 = MovAleatorio(ponderacion=config.pesoMovAleatorio)
        return sum([regla1,regla2,regla3,regla4])


def ReglaSeparacion(ponderacion, factorAlejamiento, ave, vecinos):
    n = len(vecinos)
    if n > 1:
        # Vectores de diferencia apuntan en la dirección contraria a cada vecino, desde la perspectiva del ave actual
        difPosiciones = np.array([vectorDifToro(ave.pos,otraAve.pos) for otraAve in vecinos])
        magnitudes = np.array([ave.calcDistancia(otraAve) for otraAve in vecinos])
        magnitudes[magnitudes==0] = 0.000001
        # Obtener vectores unitarios que apuntan en la direccion contraria a cada vecino
        dirNormalizadas = difPosiciones / magnitudes[:, np.newaxis] # Trasponer el vector de magnitudes (para que quede como vector columna)
        # Obtener un vector
        vel = np.sum(dirNormalizadas * (factorAlejamiento/magnitudes)[:, np.newaxis], axis=0)
    else:
        vel = np.array([0, 0])
    return vel * ponderacion


def ReglaAlineamiento(ponderacion, vecinos):
    if len(vecinos)< 1:
        return np.array([0,0])
    # Obtener los vectores de velocidad de las aves cercanas
    velocidades = np.array([b.vel for b in vecinos])
    # Obtener las magnitudes de cada vector
    magnitudes = np.sum(np.abs(velocidades) ** 2, axis=-1) ** (1. / 2)
    magnitudes[magnitudes==0] = 1 # Convertir las magnitudes cero en cualquier numero para que no haya div por cero
    # Obtener vectores de velocidad normalizados
    velNormalizadas: np.ndarray = velocidades / magnitudes[:, np.newaxis]
    # Promedio de las direcciones de las aves cercanas, sin contar su magnitud, solo su direccion
    vel: np.ndarray = velNormalizadas.mean(axis=0)
    return vel * ponderacion


def ReglaCohesion(ponderacion, ave, vecinos):
    if len(vecinos) == 0:
        return np.array([0, 0])
    # "Centro de gravedad" de las aves cercanas: AQUI ESTA EL PROBLEMA
    # COMO LAS AVES QUE PASAN POR EL BORDE TIENEN UNA POSICION AL OTRO LADO, TIRAN PARA ATRAS A SUS VECINOS
    # posPromedio = np.array([b.pos for b in vecinos]).mean(axis=0)
    posPromedio = 0
    for otraAve in vecinos:
        posVecino = ave.pos + vectorDifToro(otraAve.pos,ave.pos)
        posPromedio += posVecino
    posPromedio = posPromedio / len(vecinos)
    diff = vectorDifToro(posPromedio, ave.pos) # vector que apunta desde el ave al centro de gravedad
    #diff = posPromedio - ave.pos
    mag = np.linalg.norm(diff)
    if mag == 0:
        return np.array([0, 0])
    return ponderacion * diff / mag # Retornar vector unitario que al centro de gravedad, ponderado por el factor recibido


def MovAleatorio(ponderacion):
    return np.random.uniform(-1, 1, 2)*ponderacion


def calcDistToro(P1, P2):
    # Obtener la distancia entre 2 puntos considerando las condiciones de borde periodicas
    distX = abs(P1[0] - P2[0])
    distY = abs(P1[1] - P2[1])
    if distX > config.mapWidth/2:
        distX = config.mapWidth - distX
    if distY > config.mapHeight/2:
        distY = config.mapHeight - distY
    dist = np.linalg.norm([distX,distY])
    return dist

def vectorDifToro(P1, P2):
    # Obtener un vector que apunta desde P2 a P1, considerando condiciones de borde periodicas
    distX = P1[0] - P2[0]
    distY = P1[1] - P2[1]
    # Ver si la distancia en uno de los ejes es mayor que la mitad del plano, se "va por el otro lado"
    if abs(distX) > config.mapWidth/2:
        # Esto implica invertir la dirección de movimiento en ese eje también
        if distX > 0:
            distX = -(config.mapWidth - abs(distX))
        else:
            distX = (config.mapWidth - abs(distX))
    if abs(distY) > config.mapHeight/2:
        if distY > 0:
            distY = -(config.mapWidth - abs(distY))
        else:
            distY = (config.mapWidth - abs(distY))
    return np.array([distX, distY])
