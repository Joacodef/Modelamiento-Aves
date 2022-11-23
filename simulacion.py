import pygame
import config
from ave import Bandada, ReglaSeparacion, ReglaAlineamiento, ReglaCohesion, MovAleatorio

pygame.init()

def main():
    pygame.display.set_caption("Aves")
    win = pygame.display.set_mode((config.mapWidth, config.mapHeight))

    bandada = Bandada()
    reglasBandada = [
        ReglaSeparacion(ponderacion=1, push_force=config.areaAlejamiento),
        ReglaAlineamiento(ponderacion=1),
        ReglaCohesion(ponderacion=0.5),
        MovAleatorio(ponderacion=1)        
    ]
    bandada.generarAves(config.numAves, reglas=reglasBandada, radioLocal=config.areaDeteccion, velMax=config.aveVelMax)

    aves = bandada.aves
    tick_length = int(1000/config.tickRate)

    ultimoTick = pygame.time.get_ticks()
    while config.running:
        win.fill(config.colorFondo)
        tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick
        if tiempoUltimoTick < tick_length:
            pygame.time.delay(tick_length - tiempoUltimoTick)

        tiempoUltimoTick = pygame.time.get_ticks() - ultimoTick

        ultimoTick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.running = False

        # Cada vez que se hace esto, se calculan las distancias entre todas las aves (O(n**2)), para determinar cuales estan cerca:
        for ave in aves:
            ave.actualizar(win, tiempoUltimoTick/1000) 

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
