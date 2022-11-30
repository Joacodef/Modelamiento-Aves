import random
import numpy as np
import pygame
import config

random.seed(3)

def generarAves( numAves, rapidezMax=config.aveRapidezMax):
    aveList = []
    for _ in range(numAves):
        aveList.append(Ave(pos=np.array([random.randint(0, config.mapWidth), random.randint(0, config.mapHeight)]), rapidezMax=rapidezMax))
    return aveList
        

def getvecinos(ave, grillaVecinos):
        listaRepulsion = []
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
                    if  distanciaAves < config.radioCohesion:
                        if distanciaAves < config.radioAlineamiento:
                            if distanciaAves < config.radioRepulsion:
                                listaRepulsion.append(aveV)
                            else:
                                listaAlineamiento.append(aveV)       
                        else:
                            listaCohesion.append(aveV)                                
        return [listaRepulsion,listaAlineamiento,listaCohesion]


class Ave():
    def __init__(self, pos=np.array([0, 0]), color=config.colorAves, size=config.aveSize, rapidezMax=config.aveRapidezMax):
        self.pos = pos
        self.color = color
        self.size = size
        self.rapidezMax = rapidezMax
        self._vel = np.array([0, 0])

    def bordePeriodico(self):
        if self.pos[0] > config.mapWidth:
            self.pos[0]=0
        if self.pos[0] < 0:
            self.pos[0]=config.mapWidth + self.pos[0]
        if self.pos[1] > config.mapHeight:
            self.pos[1]=0
        if self.pos[1] < 0:
            self.pos[1]=config.mapHeight + self.pos[1]

    def actualizar(self, ventana, grillaVecinos):
        self.actualizarVelPos(grillaVecinos)
        self.bordePeriodico()
        self.draw(ventana)

    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, vel):
        magnitud = np.linalg.norm(vel)
        if magnitud > self.rapidezMax:
            vel = vel * (self.rapidezMax/magnitud)
        self._vel = vel

    def draw(self, ventana):
        if config.verAves:
            if np.linalg.norm(self.vel) == 0:
                dir = np.array([1, 0]) # Direccion por defecto en la que miran los pajaros (para no cambiar su forma cuando estan detenidos)
            else:
                dir = self.vel / np.linalg.norm(self.vel)
            dir *= self.size # Vector que apunta en la direccion en la que se mueve el ave, ponderado por el tamaño especificado
            dirPerpendicular = np.cross(np.array([dir[0], dir[1], 0]), np.array([0, 0, 1]))[:2] # Obtiene un vector perpendicular a dir
            centro = self.pos
            points = [
                 dir + centro,
                 -dir + dirPerpendicular*2 + centro,
                 -dir - dirPerpendicular*2 + centro,
            ] 

            pygame.draw.polygon(ventana, self.color, points)
            if config.verAreas == True:
                pygame.draw.circle(ventana, (255,   0,   0), self.pos, config.radioRepulsion, width=1)
                pygame.draw.circle(ventana, (0,   0,   255), self.pos, config.radioAlineamiento, width=1)
                pygame.draw.circle(ventana, (0,   255,   0), self.pos, config.radioCohesion, width=1)
            
    def actualizarVelPos(self, grillaVecinos):
        # Obtener vecinos:
        vecinos = getvecinos(self, grillaVecinos) # [listaRepulsion, listaAlineamiento, listaCohesion]
        # Modificar velocidad del ave segun las reglas:
        self.calcularReglas(vecinos)
        #self.vel = np.array([0,0])
        tiempo = 1/config.tickRate
        self.pos += (self.vel * tiempo).astype(int)

    def calcularReglas(self, vecinos):
        ReglaRepulsion(ponderacion=config.pesoSeparacion, ave=self, vecinos=vecinos[0])
        ReglaAlineamiento(ponderacion=config.pesoAlineamiento, ave=self, vecinos=vecinos[1])
        ReglaCohesion(ponderacion=config.pesoCohesion, ave=self, vecinos=vecinos[2])
        MovAleatorio(ponderacion=config.pesoMovAleatorio, ave=self)

    #==========FIN CLASE AVE===========#


def ReglaRepulsion(ponderacion, ave,  vecinos):
    if len(vecinos) < 1:
        return
    else:
        difPosicionesNorm = []
        for vecino in vecinos:
            # Vectores de diferencia apuntan en la dirección contraria a cada vecino, desde la perspectiva del ave actual:
            difPosicionVec = vectorDifToro(ave.pos, vecino.pos)
            if np.max(difPosicionVec) != 0:
                difPosicionesNorm.append(difPosicionVec/np.linalg.norm(difPosicionVec)) # Se normalizan los vectores de diferencia
        difPosicionesNorm = np.array(difPosicionesNorm)
        vel = np.sum(difPosicionesNorm, axis=0) # Se suman los vectores de diferencia normalizados
        ave.vel = ave.vel + vel * config.factorRapidez * ponderacion


def ReglaAlineamiento(ponderacion, ave, vecinos):
    if len(vecinos) < 1:
        return
    else:
        velocidadesNormal = []
        for vecino in vecinos:
            # Velocidades de los vecinos normalizadas:
            if np.max(vecino.vel) != 0:
                velocidadesNormal.append(vecino.vel/np.linalg.norm(vecino.vel))
            else:
                velocidadesNormal.append(np.array([0,0]))
        velocidadesNormal = np.array(velocidadesNormal)
        vel = velocidadesNormal.mean(axis=0) # Se promedian los vectores de velocidad normalizados
        ave.vel = ave.vel + vel * config.factorRapidez * ponderacion


def ReglaCohesion(ponderacion, ave, vecinos):   
    if len(vecinos) < 1:
        return
    else:
        posPromedioV = np.array([0,0])
        for vecino in vecinos:
            posPromedioV += np.add(ave.pos,vectorDifToro(vecino.pos, ave.pos)) # Posicion promedio de los vecinos
        posPromedioV = posPromedioV/len(vecinos)
        diff = vectorDifToro(posPromedioV, ave.pos) # Vector que apunta desde el ave a la posicion promedio de los vecinos
        mag = np.linalg.norm(diff)
        if mag == 0:
            return
        vel = ponderacion * diff / mag # Vector unitario que apunta a la pos promedio de los vecinos
        ave.vel = ave.vel + vel * config.factorRapidez * ponderacion


def MovAleatorio(ponderacion, ave):
    vel = np.random.uniform(-1, 1, 2)*ponderacion
    ave.vel = ave.vel + vel * config.factorRapidez * ponderacion


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