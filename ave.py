import random
import numpy as np
import pygame
import config

random.seed(3)

def generarAves(numAves):
    aveList = []
    for _ in range(numAves):
        #aveList.append(Ave(pos=np.array([random.uniform(0.0, config.ladoMapa), random.uniform(0.0, config.ladoMapa)])))
        #aveList.append(Ave(pos=np.array([random.uniform(320, 480), random.uniform(320, 480)])))
        aveList.append(Ave(pos=np.array([random.uniform(320, 480), random.uniform(0.0, config.ladoMapa)])))
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
        for i in [posY,(posY-1)%dimYGrillaV,(posY+1)%dimYGrillaV]:
            for j in [posX,(posX-1)%dimXGrillaV,(posX+1)%dimXGrillaV]:
                for aveV in grillaVecinos[i][j]:
                    if len(listaSeparacion)>config.numMaxVecinos and len(listaAlineamiento)>config.numMaxVecinos \
                        and len(listaCohesion)>config.numMaxVecinos:
                        break
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
        vecinos = getvecinos(self, grillaVecinos) # [listaSeparacion, listaAlineamiento, listaCohesion]
        acel = self.calcularReglas(vecinos)
        self.vel += (acel - config.airDragCoeff*self.vel) 
        self.pos += self.vel
        self.bordePeriodico()
        self.draw(ventana)

    def bordePeriodico(self):
        self.pos[0] = self.pos[0]%config.ladoMapa
        self.pos[1] = self.pos[1]%config.ladoMapa

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
            while mag == 0: # Si dos aves estuvieran en la misma posición, se crea un vector aleatorio 
                dif = np.random.uniform(-1, 1, 2) # Las componentes del vector están entre -1 y 1
                mag = np.linalg.norm(dif)
            magInversa = config.radioSeparacion/mag**2 # magnitud se hace mas fuerte mientras mas cerca se este al ave
            difPosiciones.append(dif*magInversa)
        vel = np.sum(np.array(difPosiciones), axis=0) # Se suman los vectores de diferencia 
        return vel * ponderacion

def ReglaAlineamiento(ponderacion, ave, vecinos):
    if len(vecinos) < 1:
        return np.array([0.0,0.0])
    else:
        velocidades = np.array([vecino.vel for vecino in vecinos])
        velocidades -= ave.vel
        vel = velocidades.mean(axis=0)
        return vel * ponderacion

def ReglaCohesion(ponderacion, ave, vecinos):   
    if len(vecinos) < 1:
        return np.array([0.0,0.0])
    else:
        posPromedioV = np.array([0.0,0.0])
        for vecino in vecinos:
            posPromedioV += vectorDifToro(vecino.pos, ave.pos)
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
    if abs(distX) > config.ladoMapa/2:
        # Esto implica invertir la dirección de movimiento de esa componente
        if distX > 0:
            distX = -(config.ladoMapa - abs(distX))
        else:
            distX = config.ladoMapa - abs(distX)
    if abs(distY) > config.ladoMapa/2:
        if distY > 0:
            distY = -(config.ladoMapa - abs(distY))
        else:
            distY = config.ladoMapa - abs(distY)
    return np.array([distX, distY])