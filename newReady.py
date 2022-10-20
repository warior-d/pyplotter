import sys
from typing import Union
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QAction, QStackedLayout, QSlider
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon
from math import atan2, degrees, pi
import geopy
import os
from geopy import Point
from geopy.distance import geodesic, distance
import xml.etree.ElementTree as ET
import csv

def getCoordsFromKML(kmlfile):
    tree = ET.parse(kmlfile)
    root = tree.getroot()
    north = None
    west = None
    east = None
    south = None
    for elem in root[0]:
        for subelem in elem:
            if subelem.tag == 'north':
                north = subelem.text
            if subelem.tag == 'west':
                west = subelem.text
            if subelem.tag == 'east':
                east = subelem.text
            if subelem.tag == 'south':
                south = subelem.text
    coordinates = {'north': north, 'west': west, 'east': east, 'south': south}
    return coordinates


def getKMLfileName(picFile):
    PICfilename, PICfile_extension = picFile.split('.')
    KMLfile = None
    #TODO: scandir - сканирует текущую директорию!!!
    with os.scandir(os.getcwd()) as files:
        for file in files:
            if file.is_file():
                KMLfilename, KMLfile_extension = file.name.split('.')
                if (KMLfile_extension.upper() == "KML") and (KMLfilename.upper() == PICfilename.upper()):
                    KMLfile = KMLfilename + '.' + KMLfile_extension
    return KMLfile

def getCoord(grid, x_ground, y_ground, x_current, y_current):
    # https://github.com/geopy/geopy/blob/master/geopy/distance.py
    gridStep = Settings.GRID_STEP
    pixelLenght = grid / gridStep
    delta_x = x_current - x_ground
    delta_y = y_ground - y_current
    lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
    lengh_meters = lengh_pixels * pixelLenght
    rads = atan2(delta_y, -delta_x)
    rads %= 2 * pi
    degs = degrees(rads) - 90
    need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW), degs).format_decimal()
    return need_point

def distanceBetweenPointsMeters(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).meters


class Settings():
    GRID_STEP = 80
    NEED_GRID = 0
    NEED_FISHING_CIRCLE = 1
    FISHING_SIRCLE_RADIUS = 60
    FISHING_SIRCLE_QNT = 2
    MASHTAB_MIN = 1
    MASHTAB_MAX = 9
    RADIUS_EARTH_M = 6372795
    FILE_NAME = "djerjinsky_karier.jpg" #"OKA_19_160.jpg"
    FILE_DEPTH_NAME = "djer.csv"  # "OKA_19_160.jpg"
    LAT_NW = None
    LON_NW = None
    LAT_SE = None
    LON_SE = None
    DEFAULT_MASHTAB = 5
    CURRENT_MASHTAB = 5
    DEFAULT_TRANSPARENCY = 9

    GRID_SCALE = ["10", "20", "40", "80", "160", "320", "640", "1000", "2000"]
    #               1     2     3     4     5      6      7       8       9
    POS_X = None
    POS_Y = None
    POS_SHIP_X = 500
    POS_SHIP_Y = 500
    COURSE = None

    # установка текущего масштаба (1 - 9)
    def setScale(self, scale):
        self.CURRENT_MASHTAB = scale
    # получение текущего масштаба
    def getScale(self):
        return self.CURRENT_MASHTAB

    # получение цены деления сетки
    def getGridScale(self):
        return self.GRID_SCALE[self.CURRENT_MASHTAB - 1]

    def getGrid(self):
        return self.GRID_STEP

    def setImageMap(self, filename):
        self.FILE_NAME = filename
        return self.FILE_NAME

class LabelShip(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        #self.move(100, 100)
        self.setGeometry(0, 0, 1000, 1000)

    def paintEvent(self, event):
        ship_height = 10
        ship_weight = 20
        x1, y1 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y - int(ship_height / 2)
        x2, y2 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y + int(ship_height / 2)
        x3, y3 = Settings.POS_SHIP_X + int(ship_weight / 2), Settings.POS_SHIP_Y
        pixmap = QPixmap()
        painter = QPainter(pixmap)
        painter.begin(self)
        pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
        painter.setPen(pen)
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y2, x3, y3)
        painter.drawLine(x3, y3, x1, y1)
        if Settings.NEED_FISHING_CIRCLE == 1:
            centr = QPoint()
            centr.setX(Settings.POS_SHIP_X)
            centr.setY(Settings.POS_SHIP_Y)
            rad = (Settings.GRID_STEP * Settings.FISHING_SIRCLE_RADIUS) / int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
            painter.drawEllipse(centr, rad, rad)
        painter.end()
        self.setPixmap(pixmap)


class LabelGrid(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        #self.move(100, 100)
        self.setGeometry(0, 0, 1900, 1800)

    def paintEvent(self, event):
        if Settings.NEED_GRID == 1:
            pixmap = QPixmap()
            x = Settings.POS_X
            y = Settings.POS_Y
            painter = QPainter(pixmap)
            painter.begin(self)
            for i in range(-10000, 10000, Settings.GRID_STEP):
                painter.drawLine(x + i, 0, x + i, 10000)
                painter.drawLine(x - i, 0, x - i, 10000)
                painter.drawLine(0, y + i, 10000, y + i)
                painter.drawLine(0, y - i, 10000, y - i)
            painter.end()
            self.setPixmap(pixmap)



class Main(QWidget):
    mouse_old_pos = None
    label_old_pos = None
    old_pos = None
    mashtab = Settings.DEFAULT_MASHTAB
    FILE_NAME = None
    KMLfileName = getKMLfileName(Settings.FILE_NAME)


    def __init__(self):
        super().__init__()
        print("INIT")
        self.settings = Settings()

        # Получим список координат
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        self.setGeometry(0, 0, screen_width, screen_height)


        self.labelMap = QLabel(self)
        self.labelMap.move(200, 150)
        self.rescaleMap()

        #включим отслеживание мышки
        self.setMouseTracking(True)

        # Объект - Label с наложенной сеткой
        self.labelGrid = LabelGrid(self)

        # Определим РЕАЛЬНОЕ (по координатам) расстояние между точками из KML
        # И отобразим на карте!
        #TODO : возможно, ресайзить нужно backgroung...

    def setImageMap(self, filename):
        Settings.FILE_NAME = filename

    def getImageMap(self):
        return Settings.FILE_NAME

    # Отрисовка карты после выполнения действий.
    def rescaleMap(self):
        coordinatesFromFile = getCoordsFromKML(getKMLfileName(Settings.FILE_NAME))
        Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE = coordinatesFromFile['north'], coordinatesFromFile['west'], coordinatesFromFile['south'], coordinatesFromFile['east']

        real_distance_map = distanceBetweenPointsMeters(Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE)
        # Определим расстояние с учетом пикселей картинки и гридом!
        self.labelMap.clear()
        pixmap = QPixmap(Settings.FILE_NAME)
        # верхний угол - координаты labelMap
        x1, y1 = self.labelMap.pos().x(), self.labelMap.pos().y()
        # нижний угол - координаты labelMap + ширина - высота картинки
        x2, y2 = x1 + pixmap.width(), y1 + pixmap.height()
        Settings.POS_X = self.labelMap.pos().x()# + int(pixmap.width()/2)
        Settings.POS_Y = self.labelMap.pos().y()# + int(pixmap.height()/2)
        grid = int(self.settings.getGridScale())
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        #TODO: koef очень похож на DrDepth, округлять бы...
        koef = real_distance_map / lengh_meters
        # пересчитаем картинку и изменим ее
        width_new = pixmap.width() * koef
        height_new = pixmap.height() * koef
        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(pixmap.scaled(int(width_new), int(height_new), Qt.KeepAspectRatio, Qt.FastTransformation))
        print("rescale")

    def updateScale(self, scale):
        Settings.CURRENT_MASHTAB = scale
        self.rescaleMap()

    def createGrid(self):
        if Settings.NEED_GRID == 0:
            Settings.NEED_GRID = 1
            self.update()
        else:
            Settings.NEED_GRID = 0
            self.update()

    # def updateSliderScale(self):
    #     Settings.CURRENT_MASHTAB = self.scale.value()
    #     scale_grid = Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]
    #     self.rescaleMap()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = event.pos() #позиция Мыши
            self.label_old_pos = self.labelMap.pos() #позиция Карты
            print(getCoord(int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]), self.labelMap.pos().x(), self.labelMap.pos().y(), self.mouse_old_pos.x(), self.mouse_old_pos.y()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = None

    def mouseMoveEvent(self, event):
        # координаты self.labelMap.pos() - экранные пиксели
        # 80 px = 10m, 20m etc
        # latitude - (N,S) - широта - Y - увеличивается вверх
        # longitude - (E,W) - долгота - X - увеличивается направо
        if not self.mouse_old_pos:
            return
        delta = event.pos() - self.mouse_old_pos
        self.update()
        new_pos = self.label_old_pos + delta
        self.labelMap.move(new_pos)
        Settings.POS_X = new_pos.x()
        Settings.POS_Y = new_pos.y()
        #print("old_pos:", Settings.POS_X, Settings.POS_Y)
        #self.labelGrid.move(self.label_old_pos + delta)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Main()
    w.show()

    sys.exit(app.exec_())