import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams, colors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.backends.backend_qt5agg import FigureCanvas
import numpy as np
from numpy import arange
from math import cos, radians, ceil

contour_data = pd.read_csv("djer.csv", header=None, names = ['y', 'x', 'z'])
contour_data.head()
maxDepth = ceil(contour_data['z'].max())
Z = contour_data.pivot_table(index='x', columns='y', values='z').T.values
X_unique = np.sort(contour_data.x.unique())
Y_unique = np.sort(contour_data.y.unique())
X, Y = np.meshgrid(X_unique, Y_unique)
# Initialize plot objects
rcParams['toolbar'] = 'None'
#rcParams['figure.figsize'] = 20, 10 # sets plot size
fig = plt.figure()
ax = fig.add_subplot(111)
# Цветовая карта
colors = ["#990000", "#cc0000", "#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ccff33", "#99ff66", "#66ff99", "#33ffcc", "#00ffff", "#00ccff", "#0099ff", "#0066ff", "#0033ff", "#0000ff", "#0000cc", "#000099"]
cmap1 = LinearSegmentedColormap.from_list("mycmap", colors)
cmap = ListedColormap(["#990000", "#cc0000", "#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ccff33", "#99ff66", "#66ff99", "#33ffcc", "#00ffff", "#00ccff", "#0099ff", "#0066ff", "#0033ff", "#0000ff", "#0000cc", "#000099"])

# заполним массив уровней изолиний
depth_arr = []
for i in arange(0, maxDepth + 1, 0.1):
    depth_arr.append(i)
levels = np.array(depth_arr)
cpf = ax.contourf(X,Y,Z,
                  levels,
                  cmap=cmap1)
line_colors = ['black' for l in cpf.levels]
cp = ax.contour(X, Y, Z,
                levels=levels,
                colors=line_colors,
                linewidths=0.2)
print(levels)

# добавим палитру
#fig.colorbar(cpf, ax=ax)

# метки контуров
ax.clabel(cp,
          fontsize=5,
          colors=line_colors,
          levels=[0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.],
          #inline=False,
          inline_spacing=1
          )

print(min(X_unique), max(X_unique), min(Y_unique), max(Y_unique))

#plt.axis([37.85963773727417, 37.89100885391235, 55.63452959060669, 55.64212560653687 ])
plt.axis([37.865750, 37.879610, 55.634572, 55.640436])
# Generate a contour plot
#cp = ax.contour(X, Y, Z)
plt.axis('off')
#plt.axis('equal')
ax.set_position([0, 0, 1, 1])
#ax.plot(37.85963773727417, 55.63452959060669)
#ax.plot(37.89100885391235, 55.64212560653687)

#ax.set_aspect('auto', adjustable='datalim')
#plt.savefig('GOOD123.svg', bbox_inches=0)

central_lat = (min(Y_unique) + max(Y_unique)) / 2
mercator_aspect_ratio = 1/cos(radians(central_lat))
print(mercator_aspect_ratio)
ax.set_aspect(mercator_aspect_ratio)
#plt.savefig('GOOD1234.svg', bbox_inches=0)
plt.show()