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
        dimXGrillaV = len(grillaVecinos)
        dimYGrillaV = len(grillaVecinos[0])
        for i in [(posX-1)%dimXGrillaV,posX,(posX+1)%dimXGrillaV]:
            for j in [(posY-1)%dimYGrillaV,posY,(posY+1)%dimYGrillaV]:
                for aveV in grillaVecinos[i][j]:
                    distanciaAves = calcDistToro(aveV.pos, ave.pos)
                    if  distanciaAves < config.radioCohesion:
                        listaCohesion.append(aveV)
                        if distanciaAves < config.radioAlineamiento:
                            listaAlineamiento.append(aveV)
                        if distanciaAves < config.radioRepulsion:
                            listaRepulsion.append(aveV)                     
        return [listaRepulsion,listaAlineamiento,listaCohesion]


class Ave():
    def __init__(self, pos=np.array([0, 0]), color=config.colorAves, size=config.aveSize, rapidezMax=config.aveRapidezMax):
        self._pos = pos
        self.color = color
        self.size = size
        self.rapidezMax = rapidezMax
        self._vel = np.array([0, 0])
        self.numVecinosRep = 0
        self.numVecinosAli = 0
        self.numVecinosCohe = 0

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
            


    def actualizarVelPos(self, tiempoTranscurrido, grillaVecinos):
        # Obtener vecinos:
        vecinos = getvecinos(self, grillaVecinos) # [listaRepulsion, listaAlineamiento, listaCohesion]
        # Calcular direccion de movimiento:
        vectorMov = self.calcularReglas(vecinos)
        # Actualizar campos numVecinos, vel y pos:
        self.numVecinosRep = len(vecinos[0])
        self.numVecinosAli = len(vecinos[1])
        self.numVecinosCohe = len(vecinos[2])
        self.vel = self.vel + vectorMov * config.factorRapidez
        #self.vel = np.array([0,0])
        tiempo = 0
        if config.tiempoReal:
            tiempo = tiempoTranscurrido
        else:
            tiempo = 1/config.tickRate
        self._pos += (self.vel * tiempo).astype(int)


    def calcularReglas(self, vecinos):
        regla1 = ReglaRepulsion(ponderacion=config.pesoSeparacion, ave=self, fuerzaEmpuje=config.fuerzaEmpuje, vecinos=vecinos[0])
        regla2 = ReglaAlineamiento(ponderacion=config.pesoAlineamiento, vecinos=vecinos[1])
        regla3 = ReglaCohesion(ponderacion=config.pesoCohesion, ave = self, vecinos=vecinos[2])
        regla4 = MovAleatorio(ponderacion=config.pesoMovAleatorio)
        #print("Para el ave en posicion",self.pos,"los valores de las reglas son: ",regla1, regla2, regla3, regla4)
        return sum([regla1, regla2, regla3, regla4])

    #==========FIN CLASE AVE===========#


def ReglaRepulsion(ponderacion, ave, fuerzaEmpuje, vecinos):
    n = len(vecinos)
    if n > 1:
        difPosiciones = []
        magnitudes = []
        for vecino in vecinos:
            # Vectores de diferencia apuntan en la dirección contraria a cada vecino, desde la perspectiva del ave actual:
            difPosicionV = vectorDifToro(ave.pos, vecino.pos)
            difPosiciones.append(difPosicionV)
            # Distancias a cada vecino:
            distV = ave.calcDistancia(vecino)
            if distV == 0:
                magnitudes.append(0.0001)
            else:
                magnitudes.append(distV)
        difPosiciones = np.array(difPosiciones)
        magnitudes = np.array(magnitudes)
        # Obtener vectores unitarios que apuntan en la direccion contraria a cada vecino
        dirNormalizadas = difPosiciones / magnitudes[:, np.newaxis] # Trasponer el vector de magnitudes (para que quede como vector columna)
        # Obtener la suma de los vectores, de manera que los que esten mas cerca pesen mas, y se ponderan ademas por una fuerza de empuje
        vel = np.sum(dirNormalizadas * (fuerzaEmpuje/magnitudes)[:, np.newaxis], axis=0)
    else:
        vel = np.array([0, 0])
    return vel * ponderacion


def ReglaAlineamiento(ponderacion, vecinos):
    velocidadesV = []
    magnitudesVelV = []
    if len(vecinos)< 1:
        return np.array([0,0])
    for vecino in vecinos:
             # Velocidades de los vecinos (componentes separadas):
            velocidadesV.append(vecino.vel)
            # Magnitudes de las velocidades de los vecinos:
            magnitudVel = (vecino.vel[0]**2 + vecino.vel[1]**2)**0.5
            if magnitudVel==0:
                magnitudesVelV.append(0.0001)
            else:
                magnitudesVelV.append(magnitudVel)
    velocidadesV = np.array(velocidadesV)
    magnitudesVelV = np.array(magnitudesVelV)
    # Obtener vectores de velocidad normalizados
    velNormalizadas: np.ndarray = velocidadesV / magnitudesVelV[:, np.newaxis]
    # Promedio de las direcciones de las aves cercanas, sin contar su magnitud, solo su direccion
    vel: np.ndarray = velNormalizadas.mean(axis=0)
    return vel * ponderacion


def ReglaCohesion(ponderacion, ave, vecinos):
    posPromedioV = np.array([0,0])
    if len(vecinos) == 0:
        return np.array([0, 0])
    for vecino in vecinos:
        posPromedioV += np.add(ave.pos,vectorDifToro(vecino.pos, ave.pos))
    posPromedioV = posPromedioV/len(vecinos)
    diff = vectorDifToro(posPromedioV, ave.pos) # vector que apunta desde el ave al centro de gravedad
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
