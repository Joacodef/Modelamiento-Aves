import random
import numpy as np
import pygame
import config

random.seed(3)

def generarAves(numAves):
    aveList = []
    for _ in range(numAves):
        aveList.append(Ave(pos=np.array([random.uniform(0.0, config.mapWidth), random.uniform(0.0, config.mapHeight)])))
    return aveList
        

def getvecinos(ave, grillaVecinos):
        listaSeparacion = []
        listaAlineamiento = []
        listaCohesion = []
        posX = int(ave.pos[0]/config.radioCohesion)
        posY = int(ave.pos[1]/config.radioCohesion)
        dimXGrillaV = len(grillaVecinos[0])
        dimYGrillaV = len(grillaVecinos)
        if posX > dimXGrillaV-1:
            posX -= 1
        if posY > dimYGrillaV-1:
            posY -= 1
        for i in [(posY-1)%dimYGrillaV,posY,(posY+1)%dimYGrillaV]:
            for j in [(posX-1)%dimXGrillaV,posX,(posX+1)%dimXGrillaV]:
                for aveV in grillaVecinos[i][j]:
                    distanciaAves = np.linalg.norm(vectorDifToro(aveV.pos, ave.pos))
                    if distanciaAves == 0.0:
                        continue
                    if  distanciaAves < config.radioCohesion:
                        if distanciaAves < config.radioAlineamiento:
                            if distanciaAves < config.radioSeparacion:
                                listaSeparacion.append(aveV)
                            else:
                                listaAlineamiento.append(aveV)       
                        else:
                            listaCohesion.append(aveV)                                
        return [listaSeparacion,listaAlineamiento,listaCohesion]


class Ave():
    def __init__(self, pos=np.array([0.0, 0.0])):
        self.pos = pos
        self.vel = np.array([0.0, 0.0])

    def actualizar(self, ventana, grillaVecinos):
        # Obtener vecinos:
        vecinos = getvecinos(self, grillaVecinos) # [listaSeparacion, listaAlineamiento, listaCohesion]
        deltaV = self.calcularReglas(vecinos)
        self.vel += deltaV
        rapi = np.linalg.norm(self.vel) 
        if rapi > config.maxRapidez:
            self.vel = config.maxRapidez*self.vel/rapi
        self.pos += self.vel
        self.bordePeriodico()
        #print("Num Vecinos del ave en:",self.pos," = ",len(vecinos[0])+len(vecinos[1])+len(vecinos[2]))
        #print("Los Vecinos son:",[vecino.pos for vecino in vecinos[0]],[vecino.pos for vecino in vecinos[1]],[vecino.pos for vecino in vecinos[2]])
        self.draw(ventana)

    def bordePeriodico(self):
        self.pos[0] = self.pos[0]%config.mapWidth
        self.pos[1] = self.pos[1]%config.mapHeight

    def draw(self, ventana):
        if config.verAves:
            if np.linalg.norm(self.vel) == 0:
                dir = np.array([1, 0]) # Direccion por defecto en la que miran los pajaros (para no cambiar su forma cuando estan detenidos)
            else:
                dir = self.vel / np.linalg.norm(self.vel)
            dir *= config.aveSize # Vector que apunta en la direccion en la que se mueve el ave, ponderado por el tamaño especificado
            dirPerpendicular = np.cross(np.array([dir[0], dir[1], 0]), np.array([0, 0, 1]))[:2] # Obtiene un vector perpendicular a dir
            centro = self.pos.astype(int)
            points = [
                 dir + centro,
                 -dir + dirPerpendicular*2 + centro,
                 -dir - dirPerpendicular*2 + centro,
            ] 

            pygame.draw.polygon(ventana, config.colorAves, points)
            if config.verAreas == True:
                pygame.draw.circle(ventana, (255,   0,   0), self.pos.astype(int), config.radioSeparacion, width=1)
                pygame.draw.circle(ventana, (0,   0,   255), self.pos.astype(int), config.radioAlineamiento, width=1)
                pygame.draw.circle(ventana, (0,   255,   0), self.pos.astype(int), config.radioCohesion, width=1)
            
    def calcularReglas(self, vecinos):
        r1 = ReglaSeparacion(ponderacion=config.pesoSeparacion, ave=self, vecinos=vecinos[0])
        r2 = ReglaAlineamiento(ponderacion=config.pesoAlineamiento, ave=self, vecinos=vecinos[1])
        r3 = ReglaCohesion(ponderacion=config.pesoCohesion, ave=self, vecinos=vecinos[2])
        r4 = MovAleatorio(ponderacion=config.pesoMovAleatorio)
        deltaV = r1+r2+r3+r4
        return deltaV


    #==========FIN CLASE AVE===========#


def ReglaSeparacion(ponderacion, ave, vecinos):
    if len(vecinos) < 1:
        return np.array([0,0])
    else:
        difPosiciones = []
        for vecino in vecinos:
            dif = vectorDifToro(ave.pos, vecino.pos)
            mag = np.linalg.norm(dif)
            while mag == 0:
                dif = np.random.uniform(-1, 1, 2)
                mag = np.linalg.norm(dif)
            magInversa = config.radioSeparacion/mag # magnitud que se hace mas fuerte mientras mas cerca se este al ave
            difPosiciones.append(dif*magInversa)
        vel = np.sum(np.array(difPosiciones), axis=0) # Se suman los vectores de diferencia 
        return vel * ponderacion


def ReglaAlineamiento(ponderacion, ave, vecinos):
    if len(vecinos) < 1:
        return np.array([0.0,0.0])
    else:
        velocidades = []
        for vecino in vecinos:
            velocidades.append(vecino.vel-ave.vel)
        velocidades = np.array(velocidades)
        vel = velocidades.mean(axis=0)
        return vel * ponderacion


def ReglaCohesion(ponderacion, ave, vecinos):   
    if len(vecinos) < 1:
        return np.array([0.0,0.0])
    else:
        posPromedioV = np.array([0.0,0.0])
        for vecino in vecinos:
            posPromedioV += np.add(ave.pos,vectorDifToro(vecino.pos, ave.pos)) # Sumar las posiciones de los vecinos (considerando cond borde periodicas)
        vel = posPromedioV/len(vecinos) # Posicion promedio de los vecinos
        return vel * ponderacion


def MovAleatorio(ponderacion):
    vel = np.random.uniform(-10, 10, 2)*ponderacion
    return vel * ponderacion


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
            distX = config.mapWidth - abs(distX)
    if abs(distY) > config.mapHeight/2:
        if distY > 0:
            distY = -(config.mapWidth - abs(distY))
        else:
            distY = config.mapWidth - abs(distY)
    return np.array([distX, distY])