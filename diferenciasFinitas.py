# Source https://levelup.gitconnected.com/solving-2d-heat-equation-numerically-using-python-3334004aa01a

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

np.seterr('raise')

# Parametros

gridSize = 100
numIteraciones = 300

delta_x = 1
delta_t = 1

lamb = 1/16

def fun(k):
    return 1

p = np.empty((numIteraciones, gridSize, gridSize))

# Condiciones iniciales:
p.fill(0.0)
for i in range(int(gridSize/2)-10,int(gridSize/2)+10):
    for j in range(int(gridSize/2)-10,int(gridSize/2)+10):
        p[0][i][j] = 2000.0

# Calculo de diferencias finitas:
def calculate(p):
    for k in range(0, numIteraciones-1, 1):
        for i in range(1, gridSize-1, delta_x):
            for j in range(1, gridSize-1, delta_x):
                try:
                    p[k + 1, i, j] = 2 * lamb * fun(k) * (delta_t / delta_x**2) * (p[k][i+1][j] + p[k][i-1][j] + p[k][i][j+1] + \
                        p[k][i][j-1] - 4*p[k][i][j]) + p[k][i][j]
                except:
                    print("Error, valores:",p[k][i+1][j],p[k][i-1][j],p[k][i][j+1],p[k][i][j-1],p[k][i][j])
                    return p
    return p

def plotheatmap(u_k, k):
    plt.clf()

    plt.title(f"Densidad en t = {k*delta_t:.3f}")
    plt.xlabel("x")
    plt.ylabel("y")

    plt.pcolormesh(u_k, cmap=plt.cm.jet, vmin=0, vmax=500)
    plt.colorbar()
    #plt.show()
    return plt

def animate(k):
    plotheatmap(p[k], k)

print("Calculo de densidad mediante diferencias finitas")

p = calculate(p)

print("calculos terminados")

anim = animation.FuncAnimation(plt.figure(), animate, interval=60, frames=300, repeat=False)
anim.save("solucion_ecuacion.gif")

f = open("registroDF.txt","w")

for k in range(0, numIteraciones-1, 1):
    f.write(str(p[k][40][40])+",")



















"""MI INTENTO
print("2D heat equation solver")

gridSize = 800
numIteraciones = 300

alpha = 2
delta_x = 10

delta_t = (delta_x ** 2)/(4 * alpha)
gamma = (alpha * delta_t) / (delta_x ** 2)

# Initialize solution: the grid of p(k, i, j)
p = np.empty((numIteraciones, int(gridSize), int(gridSize)))

# Initial condition everywhere inside the grid
u_initial = 0

# Set the initial condition
p.fill(u_initial)
for i in range(350,451):
    for j in range(350,451):
        p[0][i][j] = 100.0

def calculate(p):
    for k in range(0, numIteraciones-1, 1):
        for i in range(1, gridSize-1, delta_x):
            for j in range(1, gridSize-1, delta_x):
                p[k + 1, i, j] = gamma * (p[k][i+1][j] + p[k][i-1][j] + p[k][i][j+1] + p[k][i][j-1] - 4*p[k][i][j]) + p[k][i][j]
    return p

def plotheatmap(u_k, k):
    # Clear the current plot figure
    plt.clf()

    plt.title(f"Temperature at t = {k*delta_t:.3f} unit time")
    plt.xlabel("x")
    plt.ylabel("y")

    # This is to plot u_k (p at time-step k)
    plt.pcolormesh(u_k, cmap=plt.cm.jet, vmin=0, vmax=100)
    plt.colorbar()

    plt.show()

# Do the calculation here
p = calculate(p)

print("p calculado")

for k in range(0,100):
    plotheatmap(p[k], k)
"""












"""COSAS DE ARCHIVOS
f = open("datosDF.txt","w")
for datosTiempoK in p:
    f.write(str(datosTiempoK[400][400])+",")
    f.write(str(datosTiempoK[420][420])+",")
    f.write(str(datosTiempoK[380][380])+";")
f.close()"""


"""
contador = 0
for datosTiempoK in p:
    for posX in datosTiempoK:
        for posY in posX:
            f.write(str(posY)+",")
        f.write(";")
    f.write("\n")
    contador += 1
    if contador % 100 == 0:
        print("Ya van",contador,"iteraciones llenando el archivo")
"""

