import pygame
import config
import numpy as np
from ave import Bandada

pygame.init()

pygame.display.set_caption("Aves")
ventana = pygame.display.set_mode((config.mapWidth, config.mapHeight))

bandada = Bandada()
bandada.generarAves(config.numAves, radioLocal=config.areaDeteccion, velMax=config.aveVelMax)
aves = bandada.aves

duracionTickMs = int(1000/config.tickRate) # Convertir a milisegundos
ultimoTick = pygame.time.get_ticks()
contador = 0

anchoCasilla = config.mapWidth/config.numDivisionesLado
altoCasilla = config.mapHeight/config.numDivisionesLado

while config.running:
    # Grilla que se resetea, rellena con [numAves, velocidad[0], velocidad[1]]:
    grilla = np.full((config.numDivisionesLado,config.numDivisionesLado,3), [0,0,0])
    ventana.fill(config.colorFondo)
    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick
    if tiempoUltimoTick < duracionTickMs:
        pygame.time.delay(duracionTickMs - tiempoUltimoTick) # Esperar a que se cumpla la duracion de un tick para pasar al siguiente

    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick

    ultimoTick = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            config.running = False
    
    """aveContador = 0
    contador += 1
    if contador == 31:
        contador = 0"""
    for ave in aves:
        """aveContador += 1
        if contador == 30:
            print("Ave",aveContador,": posicion - ",ave.pos," velocidad - ",ave.vel," coordenadas en grilla - ", coordG)"""
        coordG = [int((ave.pos[1]-1)/altoCasilla),int((ave.pos[0]-1)/anchoCasilla)] # Notar que las posiciones en la grilla son (fila, columna) y en el mapa son (x, y) (están al revés)
        ave.actualizar(ventana, tiempoUltimoTick/1000)
        # Sumarle 1 al contador de aves de esa casilla
        grilla[coordG[0],coordG[1]][0] += 1
        # Sumar un total de velocidad horizontal y vertical (para después sacar el promedio)
        grilla[coordG[0],coordG[1]][1] += ave.vel[0]
        grilla[coordG[0],coordG[1]][2] += ave.vel[1]
    
    # Mostrar Lineas de la grilla
    if config.verGrilla:
        for i in range(1,config.numDivisionesLado):
            pygame.draw.line(ventana, config.colorLinea, (i * config.mapWidth/config.numDivisionesLado,0), (i * config.mapWidth/config.numDivisionesLado, config.mapHeight))
            pygame.draw.line(ventana, config.colorLinea, (0,i * config.mapHeight/config.numDivisionesLado), (config.mapWidth, i * config.mapHeight/config.numDivisionesLado))

    # Mostrar Numeros de la grilla
    for i in range(0,config.numDivisionesLado):    
        for j in range(0,config.numDivisionesLado):
            if grilla[i][j][0] != 0:
                    grilla[i][j][1] /= grilla[i][j][0] # Sacar el promedio de velocidad horizontal (vel[0]/numAvesEnCasilla) 
                    grilla[i][j][2] /= grilla[i][j][0] # Sacar el promedio de velocidad vertical
            if config.verValoresGrilla:
                font = pygame.font.SysFont('arial', 20)
                text = font.render(str(grilla[i][j]), True, (0, 0, 0))
                ventana.blit(text, [j*anchoCasilla+anchoCasilla/2-30,i*altoCasilla+altoCasilla/2-15])
    pygame.display.flip()

pygame.quit()
