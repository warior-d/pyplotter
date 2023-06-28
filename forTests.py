import pandas as pd
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QWidget, QStackedLayout
import numpy as np
from numpy import arange
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import rcParams, colors
import random
from math import cos, radians, ceil
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
import time

class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        geometry = app.desktop().availableGeometry()
        #self.setGeometry(geometry)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.figure = plt.figure()
        self.figure.set_alpha(0)
        self.canvas = FigureCanvas(self.figure)
        self.plot()

        layout = QStackedLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self):

        ''' plot some random stuff '''
        self.figure.patch.set_facecolor("None")
        tic1 = time.perf_counter()
        contour_data = pd.read_csv("djer.csv", header=None, names=['y', 'x', 'z'])
        #print("1", contour_data.head())
        #print(contour_data.head())   55.634572, 55.640436
        l = contour_data[(37.879610 <= contour_data['x']) & \
                           (37.865750 >= contour_data['x']) & \
                           (55.634572 <= contour_data['y'])  & \
                           (55.640436 >= contour_data['y'])]
        # 37.865750, 37.879610, 55.634572, 55.640436

        print("1 all", contour_data.size)

        df = contour_data[(contour_data['x'] > 37.865750) & (contour_data['x'] < 37.879610) & (contour_data['y'] > 55.634572) & (contour_data['y'] < 55.640436)]
        print("1 df", df.size)

        Zz = df.pivot_table(index='x', columns='y', values='z').T.values
        print("SIZE DEFAULT Zz: ", Zz.size)
        Xx_unique = np.sort(df.x.unique())
        Yy_unique = np.sort(df.y.unique())
        Xn, Yn = np.meshgrid(Xx_unique, Yy_unique)

        maxDepth = ceil(contour_data['z'].max())
        Z = contour_data.pivot_table(index='x', columns='y', values='z').T.values
        print("SIZE DEFAULT Z: ", Z.size)

        X_unique = np.sort(contour_data.x.unique())
        print("lena", len(X_unique))
        Y_unique = np.sort(contour_data.y.unique())
        #xc = np.where((X_unique>=37.865750) & (X_unique<=37.879610))
        #print("lena2", len(xc[0]))
        X, Y = np.meshgrid(X_unique, Y_unique)
        #print(X)


        rcParams['toolbar'] = 'None'
        # rcParams['figure.figsize'] = 20, 10 # sets plot size
        ax = self.figure.add_subplot(111)
        # Цветовая карта
        colors = ["#990000", "#cc0000", "#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ccff33", "#99ff66",
                  "#66ff99", "#33ffcc", "#00ffff", "#00ccff", "#0099ff", "#0066ff", "#0033ff", "#0000ff", "#0000cc",
                  "#000099"]
        cmap1 = LinearSegmentedColormap.from_list("mycmap", colors)
        cmap = ListedColormap(
            ["#990000", "#cc0000", "#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ccff33", "#99ff66",
             "#66ff99", "#33ffcc", "#00ffff", "#00ccff", "#0099ff", "#0066ff", "#0033ff", "#0000ff", "#0000cc",
             "#000099"])

        depth_arr = []
        for i in arange(0, maxDepth + 1, 1):
            depth_arr.append(i)
        levels = np.array(depth_arr)
        cpf = ax.contourf(Xn, Yn, Zz,
                          levels,
                          cmap=cmap)
        line_colors = ['black' for l in cpf.levels]
        cp = ax.contour(Xn, Yn, Zz,
                        levels=levels,
                        colors=line_colors,
                        linewidths=0.3)
        ax.clabel(cp,
                  fontsize=7,
                  colors=line_colors,
                  # inline=False,
                  inline_spacing=1
                  )
        ax.set_position([0, 0, 1, 1])
        central_lat = (min(Y_unique) + max(Y_unique)) / 2
        mercator_aspect_ratio = 1 / cos(radians(central_lat))
        #print(mercator_aspect_ratio)
        ax.set_aspect(mercator_aspect_ratio)
        plt.axis('off')
        #plt.axis([37.865750, 37.879610, 55.634572, 55.640436])
        #plt.patch.set_alpha(0)
        # refresh canvas
        ax.patch.set_alpha(0)
        self.canvas.draw()
        self.canvas.setStyleSheet("background-color:transparent;")
        tic2 = time.perf_counter()
        print("time:", tic2-tic1)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())