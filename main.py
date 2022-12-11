import pygame
import config
import numpy as np
import ave as Ave

dimXGrillaV = int(config.ladoMapa/config.radioCohesion)
dimYGrillaV = int(config.ladoMapa/config.radioCohesion)
file = open("registro.txt", 'w')

def rellenarGrillaVecinos(aves):
    grillaVecinos = []
    for i in range(0,dimYGrillaV):
        grillaVecinos.append([])
        for _ in range(0,dimXGrillaV):
            grillaVecinos[i].append([])
    for ave in aves:
        posXAve = int(ave.pos[0]/config.radioCohesion)
        posYAve = int(ave.pos[1]/config.radioCohesion)
        if posXAve+1 > dimXGrillaV:
            posXAve -= 1            
        if posYAve+1 > dimYGrillaV:
            posYAve -= 1
        #print("Ave puesta en posicion:",int(np.floor(ave.pos[0]/config.radioCohesion)),int(np.floor(ave.pos[1]/config.radioCohesion)))
        grillaVecinos[posYAve][posXAve].append(ave)
    return grillaVecinos

pygame.init()

pygame.display.set_caption("Aves")
ventana = pygame.display.set_mode((config.ladoMapa, config.ladoMapa))

aves = Ave.generarAves(config.numAves)

anchoCasilla = config.ladoMapa/config.numDivisionesLado
altoCasilla = config.ladoMapa/config.numDivisionesLado

clock = pygame.time.Clock()

#maxRapidez = 0.0

while config.running:
    # Grilla de campos se resetea, rellena con [numAves, velocidad[0], velocidad[1]]:
    grillaCampo = np.full((config.numDivisionesLado,config.numDivisionesLado,3), [0,0,0])

    ventana.fill(config.colorFondo)

    # Para salir del juego
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            config.running = False

    grillaVecinos = rellenarGrillaVecinos(aves)
    
    # Actualización de las aves:
    for ave in aves:
        coordG = [int((ave.pos[1]-1)/altoCasilla),int((ave.pos[0]-1)/anchoCasilla)] # Notar que las posiciones en la grilla son (fila, columna) y en el mapa son (x, y) (están al revés)
        ave.actualizar(ventana, grillaVecinos)
        # Sumarle 1 al contador de aves de esa casilla
        grillaCampo[coordG[0],coordG[1]][0] += 1
        # Sumar un total de velocidad horizontal y vertical (para después sacar el promedio)
        grillaCampo[coordG[0],coordG[1]][1] += ave.vel[0]
        grillaCampo[coordG[0],coordG[1]][2] += ave.vel[1]
        """if maxRapidez < np.linalg.norm(ave.vel):
            maxRapidez = np.linalg.norm(ave.vel)
            print("max rapi",maxRapidez)"""

    # Mostrar líneas de la grilla de velocidades y densidad:
    if config.verGrillaCampos:
        for i in range(1,config.numDivisionesLado):
            pygame.draw.line(ventana, config.colorLinea, (i * config.ladoMapa/config.numDivisionesLado,0), (i * config.ladoMapa/config.numDivisionesLado, config.ladoMapa))
            pygame.draw.line(ventana, config.colorLinea, (0,i * config.ladoMapa/config.numDivisionesLado), (config.ladoMapa, i * config.ladoMapa/config.numDivisionesLado))

    # Mostrar líneas de la grilla de vecinos:
    if config.verGrillaVecinos:
        for i in range(1,dimYGrillaV):
            pygame.draw.line(ventana, config.colorLinea, (i * config.radioCohesion,0), (i * config.radioCohesion, config.ladoMapa))
        for j in range(1,dimXGrillaV):
            pygame.draw.line(ventana, config.colorLinea, (0,j * config.radioCohesion), (config.ladoMapa, j * config.radioCohesion))

    # Actualizar y guardar datos de grilla de campos:
    for i in range(0,config.numDivisionesLado):    
        for j in range(0,config.numDivisionesLado):
            if grillaCampo[i][j][0] != 0:
                    grillaCampo[i][j][1] /= grillaCampo[i][j][0] # Sacar el promedio de velocidad horizontal (vel[0]/numAvesEnCasilla) 
                    grillaCampo[i][j][2] /= grillaCampo[i][j][0] # Sacar el promedio de velocidad vertical
            file.write(str(i)+","+str(j)+","+str(grillaCampo[i][j][0])+","+str(grillaCampo[i][j][1])+","+str(grillaCampo[i][j][2])+";")
            
            # Mostrar números de la grilla de velocidades y densidad:
            if config.verValoresGrillaCampos:
                font = pygame.font.SysFont('arial', config.fontSize)
                text = font.render(str(grillaCampo[i][j]), True, (0, 0, 0))
                ventana.blit(text, [j*anchoCasilla+anchoCasilla/2-30,i*altoCasilla+altoCasilla/2-15])
    file.write("\n")

    #Limitar a 30 los cuadros por segundo (fps):
    clock.tick(30)

    # Cacular fps actuales:
    font = pygame.font.SysFont("Arial", 18)
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    ventana.blit(fps_text,[10,10])

    pygame.display.flip()

pygame.quit()
file.close()


