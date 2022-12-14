import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

NUM_CASILLA = 12
NUM_CASILLA_SUP = (NUM_CASILLA-5)%25
NUM_CASILLA_INF = (NUM_CASILLA+5)%25
NUM_CASILLA_IZQ = (NUM_CASILLA-1)%5+(NUM_CASILLA-NUM_CASILLA%5)
NUM_CASILLA_DER = (NUM_CASILLA+1)%5+(NUM_CASILLA-NUM_CASILLA%5)

DENSIDAD = 2
VELOCIDAD_HOR = 3
VELOCIDAD_VERT = 4

DATA = DENSIDAD

df = pd.read_csv("registro5.txt",sep=";",header=None)
casilla = []
casilla_sup = []
casilla_inf = []
casilla_izq = []
casilla_der = []

for data in df[NUM_CASILLA]:
    numeros = data.split(",")
    #casilla.append([int(numeros[2]),int(numeros[3]),int(numeros[4])])
    casilla.append(float(numeros[DATA]))
for data in df[NUM_CASILLA_SUP]:
    numeros = data.split(",")
    #casilla.append([int(numeros[2]),int(numeros[3]),int(numeros[4])])
    casilla_sup.append(float(numeros[DATA]))
for data in df[NUM_CASILLA_INF]:
    numeros = data.split(",")
    #casilla.append([int(numeros[2]),int(numeros[3]),int(numeros[4])])
    casilla_inf.append(float(numeros[DATA]))
for data in df[NUM_CASILLA_DER]:
    numeros = data.split(",")
    #casilla.append([int(numeros[2]),int(numeros[3]),int(numeros[4])])
    casilla_der.append(float(numeros[DATA]))
for data in df[NUM_CASILLA_IZQ]:
    numeros = data.split(",")
    #casilla.append([int(numeros[2]),int(numeros[3]),int(numeros[4])])
    casilla_izq.append(float(numeros[DATA]))
#print(casillaCero)

ticks = list(range(0,len(casilla)))
casilla = np.array(casilla)

plt.plot(ticks,casilla)
#plt.plot(ticks,casilla_izq)
#plt.plot(ticks,casilla_der)
#plt.plot(ticks,casilla_inf)
#plt.plot(ticks,casilla_sup)

plt.xlabel('Ticks')
plt.ylabel('Número de Aves')

plt.legend(['densidad casilla '+str(NUM_CASILLA)]) #,'casilla izquierda','casilla derecha' 

plt.show()