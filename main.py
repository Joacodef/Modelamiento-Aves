import pygame
import config
import numpy as np
from ave import Bandada

dimXGrillaV = int(np.ceil(config.mapWidth/config.radioDeteccion))
dimYGrillaV = int(np.ceil(config.mapHeight/config.radioDeteccion))

def rellenarGrillaVecinos(aves):
    grillaVecinos = []
    for i in range(0,dimXGrillaV):
        grillaVecinos.append([])
        for j in range(0,dimYGrillaV):
            grillaVecinos[i].append([])
    for ave in aves:
        #print("Ave en posicion: ", ave.pos)
        if ave.pos[0] == config.mapWidth:
            ave.pos[0] = 0
        if ave.pos[1] == config.mapHeight:
            ave.pos[1] = 0
        #print("Ave puesta en posicion:",int(np.floor(ave.pos[0]/config.radioDeteccion)),int(np.floor(ave.pos[1]/config.radioDeteccion)))
        grillaVecinos[int(ave.pos[0]/config.radioDeteccion)][int(ave.pos[1]/config.radioDeteccion)].append(ave)
    return grillaVecinos

pygame.init()

pygame.display.set_caption("Aves")
ventana = pygame.display.set_mode((config.mapWidth, config.mapHeight))

bandada = Bandada()
bandada.generarAves(config.numAves, radioLocal=config.radioDeteccion, velMax=config.aveVelMax)
aves = bandada.aves

duracionTickMs = int(1000/config.tickRate) # Convertir a milisegundos
ultimoTick = pygame.time.get_ticks()

anchoCasilla = config.mapWidth/config.numDivisionesLado
altoCasilla = config.mapHeight/config.numDivisionesLado

while config.running:
    # Grilla que se resetea, rellena con [numAves, velocidad[0], velocidad[1]]:
    grillaCampo = np.full((config.numDivisionesLado,config.numDivisionesLado,3), [0,0,0])
    # grillaVecinos = np.full((int(np.ceil(config.mapWidth/config.radioDeteccion)),int(np.ceil(config.mapHeight/config.radioDeteccion))),[])
    ventana.fill(config.colorFondo)
    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick
    if tiempoUltimoTick < duracionTickMs:
        pygame.time.delay(duracionTickMs - tiempoUltimoTick) # Esperar a que se cumpla la duracion de un tick para pasar al siguiente

    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick

    ultimoTick = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            config.running = False
    
    grillaVecinos = rellenarGrillaVecinos(aves)

    for ave in aves:
        coordG = [int((ave.pos[1]-1)/altoCasilla),int((ave.pos[0]-1)/anchoCasilla)] # Notar que las posiciones en la grilla son (fila, columna) y en el mapa son (x, y) (están al revés)
        ave.actualizar(ventana, tiempoUltimoTick/1000, grillaVecinos)
        # Sumarle 1 al contador de aves de esa casilla
        grillaCampo[coordG[0],coordG[1]][0] += 1
        # Sumar un total de velocidad horizontal y vertical (para después sacar el promedio)
        grillaCampo[coordG[0],coordG[1]][1] += ave.vel[0]
        grillaCampo[coordG[0],coordG[1]][2] += ave.vel[1]

    # Mostrar Lineas de la grilla
    if config.verGrilla:
        for i in range(1,config.numDivisionesLado):
            pygame.draw.line(ventana, config.colorLinea, (i * config.mapWidth/config.numDivisionesLado,0), (i * config.mapWidth/config.numDivisionesLado, config.mapHeight))
            pygame.draw.line(ventana, config.colorLinea, (0,i * config.mapHeight/config.numDivisionesLado), (config.mapWidth, i * config.mapHeight/config.numDivisionesLado))

    # Mostrar Numeros de la grilla y sacar promedio de velocidades
    for i in range(0,config.numDivisionesLado):    
        for j in range(0,config.numDivisionesLado):
            if grillaCampo[i][j][0] != 0:
                    grillaCampo[i][j][1] /= grillaCampo[i][j][0] # Sacar el promedio de velocidad horizontal (vel[0]/numAvesEnCasilla) 
                    grillaCampo[i][j][2] /= grillaCampo[i][j][0] # Sacar el promedio de velocidad vertical
            if config.verValoresGrilla:
                font = pygame.font.SysFont('arial', config.fontSize)
                text = font.render(str(grillaCampo[i][j]), True, (0, 0, 0))
                ventana.blit(text, [j*anchoCasilla+anchoCasilla/2-30,i*altoCasilla+altoCasilla/2-15])
    pygame.display.flip()

pygame.quit()


