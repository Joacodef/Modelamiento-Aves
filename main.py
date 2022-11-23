import pygame
import config
from ave import Bandada, ReglaSeparacion, ReglaAlineamiento, ReglaCohesion, MovAleatorio

pygame.init()

pygame.display.set_caption("Aves")
win = pygame.display.set_mode((config.mapWidth, config.mapHeight))

bandada = Bandada()
reglasBandada = [
    ReglaSeparacion(ponderacion=2, push_force=config.areaAlejamiento),
    ReglaAlineamiento(ponderacion=1),
    ReglaCohesion(ponderacion=0.5),
    MovAleatorio(ponderacion=1)        
]
bandada.generarAves(config.numAves, reglas=reglasBandada, radioLocal=config.areaDeteccion, velMax=config.aveVelMax)

aves = bandada.aves
duracionTickMs = int(1000/config.tickRate) # Convertir a milisegundos

ultimoTick = pygame.time.get_ticks()

contador = 0
while config.running:
    contador += 1
    win.fill(config.colorFondo)
    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick
    if tiempoUltimoTick < duracionTickMs:
        pygame.time.delay(duracionTickMs - tiempoUltimoTick) # Esperar a que se cumpla la duracion de un tick para pasar al siguiente

    tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick

    ultimoTick = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            config.running = False

    # Cada vez que se hace esto, se calculan las distancias entre todas las aves (O(n**2)), para determinar cuales estan cerca:
    #aveContador = 0
    for ave in aves:
        """aveContador += 1
        if contador == 30:
            print("Ave",aveContador,": posicion - ",ave.pos," velocidad - ",ave._v)"""
        ave.actualizar(win, tiempoUltimoTick/1000)
    """if contador == 60:
        contador = 0"""
    pygame.display.flip()

pygame.quit()
