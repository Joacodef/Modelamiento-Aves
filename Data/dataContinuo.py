import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


df = pd.read_csv("registroDF2.txt",sep=",",header=None)
datos = []

for dato in df:
    if df[dato][0] > 0.0:
        datos.append(float(df[dato][0]))

datos = np.array(datos)
ticks = list(range(0,len(datos)))

f, ax = plt.subplots(1)

ax.plot(ticks,datos)

ax.set_xlabel('Ticks')
ax.set_ylabel('Densidad')

ax.set_ylim(ymin=0)

ax.set_title("Densidad del punto central")

plt.show()