#!/usr/bin/python3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QFileDialog, QLabel, QWidget, QMainWindow, QApplication, QSlider, \
    QAction, qApp, QToolBar, QStackedWidget, QPushButton, QDesktopWidget, QComboBox, QLCDNumber
# import newReady as myWidget
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtSerialPort
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
import csv
import os
from geopy import Point
from geopy.distance import geodesic, distance
import xml.etree.ElementTree as ET
from math import atan2, degrees, pi, sin, cos, radians
from PyQt5.QtCore import Qt, QPoint, QRect, QIODevice, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon
from PyQt5.Qt import QTransform
from datetime import *


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

# по координатам реперной точки на экране дает координаты нужной точки
def getCoord(x_ground, y_ground, x_current, y_current):
    # https://github.com/geopy/geopy/blob/master/geopy/distance.py
    grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
    gridStep = Settings.GRID_STEP
    pixelLenght = grid / gridStep
    delta_x = x_current - x_ground
    delta_y = y_ground - y_current
    lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
    lengh_meters = lengh_pixels * pixelLenght
    rads = atan2(delta_y, -delta_x)
    rads %= 2 * pi
    degs = degrees(rads) - 90
    need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW),
                                                                      degs).format_decimal()
    # вывод - в координатах.
    return need_point

# расстояние в метрах между двумя координатами
def distanceBetweenPointsMeters(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).meters

# расстояние в пикселях между двумя точками на экране
def distanceInPixels(x1, y1, x2, y2):
    return ((x1 - x2) ** (2) + (y1 - y2) ** (2)) ** (0.5)


class Settings():
    GRID_STEP = 80
    NEED_GRID = 0
    NEED_FISHING_CIRCLE = 1
    FISHING_SIRCLE_RADIUS = 60
    FISHING_SIRCLE_QNT = 2
    MASHTAB_MIN = 1
    MASHTAB_MAX = 9
    FILE_NAME = None  # "OKA_19_160.jpg"
    KML_FILE_NAME = None
    FILE_DEPTH_NAME = "djer.csv"  # "OKA_19_160.jpg"
    IMAGE_WIDTH = None
    IMAGE_HEIGHT = None
    LAT_NW = None
    LON_NW = None
    LAT_SE = None
    LON_SE = None
    DEFAULT_MASHTAB = 4
    CURRENT_MASHTAB = 4
    KOEFFICIENT = None
    DEFAULT_TRANSPARENCY = 9
    DESCTOP_WIDHT = None
    DESCTOP_HEIGHT = None
    CENTR_LAT = None
    CENTR_LON = None
    # Для увеличения можно поменять обратно сделать!
    GRID_SCALE = ["10", "20", "40", "80", "160", "320", "640", "1000", "2000"]
    #               0     1     2     3     4      5      6       7       8
    #               1     2     3     4     5      6      7       8       9
    POS_X = 200
    POS_Y = 150
    POS_SHIP_X = 500
    POS_SHIP_Y = 500
    COURSE = None
    PAINT_POSx = None
    PAINT_POSy = None
    BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"] #["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"]
    BAUD_RATE = None
    COM_PORT_EKHO = None
    GPS_DEPTH_KEY = '$SDDBT'
    GPS_DATA_KEY = '$GPRMC'
    GPS_X = None
    GPS_Y = None
    KEEP_SHIP = 0

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
        # self.move(100, 100)
        self.setScaledContents(True)
        self.pix = QPixmap("icons/lodka_med.png")
        self.setPixmap(self.pix)

    def getPos(self):
        dx = self.width() / 2
        dy = self.height() / 2
        realPos = QPoint()
        realPos.setX(int(self.pos().x() + dx))
        realPos.setY(int(self.pos().y() + dy))
        return realPos

    def moveLike(self, x, y, rotate = 0):
        dx = self.width() / 2
        dy = self.height() / 2
        if rotate:
            t = QTransform().rotate(rotate)
            self.setPixmap(self.pix.transformed(t))
        self.move(int(x - dx), int(y - dy))

    # def paintEvent(self, event):
    #     ship_height = 10
    #     ship_weight = 20
    #     x1, y1 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y - int(ship_height / 2)
    #     x2, y2 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y + int(ship_height / 2)
    #     x3, y3 = Settings.POS_SHIP_X + int(ship_weight / 2), Settings.POS_SHIP_Y
    #     pixmap = QPixmap()
    #     painter = QPainter(pixmap)
    #     painter.begin(self)
    #     pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
    #     pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
    #     painter.setPen(pen)
    #     painter.drawLine(x1, y1, x2, y2)
    #     painter.drawLine(x2, y2, x3, y3)
    #     painter.drawLine(x3, y3, x1, y1)
    #     if Settings.NEED_FISHING_CIRCLE == 1:
    #         centr = QPoint()
    #         centr.setX(Settings.POS_SHIP_X)
    #         centr.setY(Settings.POS_SHIP_Y)
    #         rad = (Settings.GRID_STEP * Settings.FISHING_SIRCLE_RADIUS) / int(
    #             Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
    #         painter.drawEllipse(centr, rad, rad)
    #     painter.end()
    #     self.setPixmap(pixmap)

# постоянный Paint event
class LabelGrid(QLabel):


    # TODO: обрабатывать событие ухода с экрана - через self.label.update()
    def __init__(self, Main):
        super().__init__(parent=Main)
        self.mainuha = Main
        self.setGeometry(0, 0, Settings.DESCTOP_WIDHT, Settings.DESCTOP_HEIGHT)
        self.IsModyfied = True
        self.moving = QPoint()
        self.posLabelMap = self.mainuha.getLabelMapPosition()
        self.lastX = self.posLabelMap.x()
        self.lastY = self.posLabelMap.y()

    def paintEvent(self, event):
        if self.IsModyfied == True:
            super().paintEvent(event)
            currentPosition = self.mainuha.getLabelMapPosition()
            #print(currentPosition)
            dx = 0
            dy = 0
            painter = QPainter(self)
            if (self.lastX != currentPosition.x()) or (self.lastY != currentPosition.y()):
                dx = self.lastX - currentPosition.x()
                dy = self.lastY - currentPosition.y()
            x = int(Settings.DESCTOP_WIDHT / 2) - dx
            y = int(Settings.DESCTOP_HEIGHT / 2) - dy
            qntX = int(Settings.DESCTOP_WIDHT / Settings.GRID_STEP)
            qntY = int(Settings.DESCTOP_HEIGHT / Settings.GRID_STEP)
            # TODO: теперь сюда нужно посчитать смещение, прибавить по X и Y!
            # докрутить!
            for i in range(int(Settings.DESCTOP_WIDHT / qntX), Settings.DESCTOP_WIDHT + abs(dx), Settings.GRID_STEP):
                painter.drawLine(x, 0, x, Settings.DESCTOP_HEIGHT)
                painter.drawLine(x + i, 0, x + i, Settings.DESCTOP_HEIGHT)
                painter.drawLine(x - i, 0, x - i, Settings.DESCTOP_HEIGHT)
            for i in range(int(Settings.DESCTOP_HEIGHT / qntY), Settings.DESCTOP_HEIGHT + abs(dy), Settings.GRID_STEP):
                painter.drawLine(0, y, Settings.DESCTOP_WIDHT, y)
                painter.drawLine(0, y + i, Settings.DESCTOP_WIDHT, y + i)
                painter.drawLine(0, y - i, Settings.DESCTOP_WIDHT, y - i)
            if Settings.PAINT_POSx is not None:
                pen = QPen(Qt.GlobalColor.yellow, 5, Qt.PenStyle.SolidLine)
                pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
                painter.setPen(pen)
                painter.drawPoint(int(Settings.PAINT_POSx), int(Settings.PAINT_POSy))
            pen = QPen(Qt.GlobalColor.green, 5, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
            painter.setPen(pen)
            painter.drawPoint(int(Settings.DESCTOP_WIDHT / 2), int(Settings.DESCTOP_HEIGHT / 2))
            self.IsModyfied = False

    def setModyfyed(self, mode):
        self.IsModyfied = mode

    def setMoving(self, delta):
        pass


class Main(QWidget):
    mouse_old_pos = None
    label_old_pos = None
    # для передвижения вместе с картой при тапе
    ship_old_pos = None
    old_pos = None
    mashtab = Settings.DEFAULT_MASHTAB
    FILE_NAME = None
    KMLfileName = Settings.KML_FILE_NAME
    # для расчета движения карты при центровке
    ship_previous_pos = []


    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)
        self.pixmapMap = QPixmap(Settings.FILE_NAME)
        # в самом начале установим координаты центральной точки в 0 - 0
        Settings.CENTR_LAT = 0
        Settings.CENTR_LON = 0
        self.posX = None
        self.posY = None
        self.supposedCentr = QPoint()
        self.doCentrPixels()
        #тут хранятся ТЕКУЩИЕ центральные координаты
        self.newCentr = ''
        # Получим список координат
        self.labelMap = QLabel(self)
        self.labelMap.move(350, 210)
        self.updateCentrPoint()
        self.addImage()

        # включим отслеживание мышки
        self.setMouseTracking(True)

        self.labelShip = LabelShip(self)
        self.labelShip.setVisible(False)


        # Объект - Label с наложенной сеткой
        self.labelGrid = LabelGrid(self)
        self.labelGrid.setVisible(False)

        self.movingCentr = False
        self.centrPoint = QPoint()
        self.centrPoint.setX(int(Settings.DESCTOP_WIDHT / 2))
        self.centrPoint.setY(int(Settings.DESCTOP_HEIGHT / 2))

        # Определим РЕАЛЬНОЕ (по координатам) расстояние между точками из KML
        # И отобразим на карте!
        # TODO : возможно, ресайзить нужно backgroung...


    def setMovingCenter(self):
        if self.movingCentr == True:
            self.movingCentr = False
            self.ship_previous_pos = []
        else:
            self.movingCentr = True


    # выдает координаты относительно ЦЕНТРА
    # ВНИМАНИЕ! Последовательность переменных играет роль!
    # Неверная последовательность приводит к противоположным координатам!!!
    def getCoordFromCentrPoint(self, x_ground, y_ground, x_current, y_current):
        grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        delta_x = x_current - x_ground
        delta_y = y_ground - y_current
        lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        rads = atan2(delta_y, -delta_x)
        rads %= 2 * pi
        degs = degrees(rads) - 90
        # toDo: заменить сеттингс на get_method!
        need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.CENTR_LAT, Settings.CENTR_LON),
                                                                          degs).format_decimal()
        # вывод - в координатах.
        return need_point

    def setImageMap(self, filename):
        Settings.FILE_NAME = filename

    def updateCentrPoint(self, newLat = 0, newLon = 0):
        # по-правильному, оно должно меняться ТОЛЬКО при перемещении
        # при рескейле - нет.
        if Settings.CENTR_LAT == 0 and Settings.CENTR_LON == 0:
            coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
            Settings.LAT_NW, Settings.LON_NW = coordinatesFromFile['north'], coordinatesFromFile['west']

            center = getCoord(self.labelMap.pos().x(), self.labelMap.pos().y(), int(Settings.DESCTOP_WIDHT / 2),
                              int(Settings.DESCTOP_HEIGHT / 2))
            newLatitude, newLongitude = center.split(', ')
            Settings.CENTR_LAT = float(newLatitude)
            Settings.CENTR_LON = float(newLongitude)
            print('initcoords',  Settings.CENTR_LAT, Settings.CENTR_LON)
        else:
            Settings.CENTR_LAT = newLat
            Settings.CENTR_LON = newLon

    def doCentrPixels(self):
        self.supposedCentr.setX(int(Settings.DESCTOP_WIDHT / 2))
        self.supposedCentr.setY(int(Settings.DESCTOP_HEIGHT / 2))

    # получить точку X, Y в текущем масштабе по геогр. координатам
    def getPointByCoordsWide(self, LatBase, LonBase, Lat, Lon, Xbase, Ybase):
        point1 = (LatBase, LonBase)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(LonBase), float(LatBase), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = Xbase + (real_dist_in_pixels * cos(bearing1))
        relY = Ybase - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getPointByCoords(self, Lat, Lon):
        point1 = (Settings.CENTR_LAT, Settings.CENTR_LON)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(Settings.CENTR_LON), float(Settings.CENTR_LAT), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = int(Settings.DESCTOP_WIDHT / 2) + (real_dist_in_pixels * cos(bearing1))
        relY = int(Settings.DESCTOP_HEIGHT / 2) - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getPointByCoordsCorner(self, Lat, Lon):
        #Settings.LAT_NW, Settings.LON_NW
        point1 = (Settings.LAT_NW, Settings.LON_NW)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(Settings.LON_NW), float(Settings.LAT_NW), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = self.labelMap.pos().x() + (real_dist_in_pixels * cos(bearing1))
        relY = self.labelMap.pos().y() - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getPointByCoordsCentr(self, LatBase, LonBase, Lat, Lon):
        point1 = (LatBase, LonBase)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(LonBase), float(LatBase), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = int(Settings.DESCTOP_WIDHT / 2) + (real_dist_in_pixels * cos(bearing1))
        relY = int(Settings.DESCTOP_HEIGHT / 2) - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getPointByCoordsALLishe(self, LatBase, LonBase, Lat, Lon, Xbase, Ybase):
        point1 = (LatBase, LonBase)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(LonBase), float(LatBase), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = int(Xbase) + (real_dist_in_pixels * cos(bearing1))
        relY = int(Ybase) - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getCoord(self, x_ground, y_ground, x_current, y_current):
        # https://github.com/geopy/geopy/blob/master/geopy/distance.py
        grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        delta_x = x_current - x_ground
        delta_y = y_ground - y_current
        lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        rads = atan2(delta_y, -delta_x)
        rads %= 2 * pi
        degs = degrees(rads) - 90
        need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW),
                                                                          degs).format_decimal()
        # вывод - в координатах.
        return need_point

    # первоначальная загрузка изображения на плоттер
    # TODO: добавить возможность передачи координаты для привязки сразу (в newWork есть идеи)
    def addImage(self):
        # первоначальное добавление картинки
        coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
        Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE = coordinatesFromFile['north'], \
                                                                             coordinatesFromFile['west'], \
                                                                             coordinatesFromFile['south'], \
                                                                             coordinatesFromFile['east']
        real_distance_map = distanceBetweenPointsMeters(Settings.LAT_NW,
                                                        Settings.LON_NW,
                                                        Settings.LAT_SE,
                                                        Settings.LON_SE)
        x1, y1 = self.labelMap.pos().x(), self.labelMap.pos().y()
        x2, y2 = x1 + self.pixmapMap.width(), y1 + self.pixmapMap.height()
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        koef = real_distance_map / lengh_meters
        width_new = self.pixmapMap.width() * koef
        height_new = self.pixmapMap.height() * koef

        # TODO: сделать добавление, чтобы по координатам был (в центре экрана - нужная координата)
        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(self.pixmapMap.scaled(int(width_new), int(height_new), Qt.KeepAspectRatio, Qt.FastTransformation))

    def getLabelMapPosition(self):
        return self.labelMap.pos()

    # увеличение / уменьшение картинки
    # TODO: возможно, добавить и смещение - отдельной функцией.
    def zoomMap(self):
        self.labelGrid.update()
        self.labelGrid.setModyfyed(True)
        # все, что ту делается - берем изначальный image, и сжимаем (растягиваем) его
        # то есть, из исходного (как есть) делаем сразу готовый.
        coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
        Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE = coordinatesFromFile['north'], \
                                                                             coordinatesFromFile['west'], \
                                                                             coordinatesFromFile['south'], \
                                                                             coordinatesFromFile['east']
        real_distance_map = distanceBetweenPointsMeters(Settings.LAT_NW,
                                                        Settings.LON_NW,
                                                        Settings.LAT_SE,
                                                        Settings.LON_SE)

        # давайте прикинем, где в текущих координатах будет край картинки
        newMapCorner = self.getPointByCoords(Settings.LAT_NW, Settings.LON_NW)
        Settings.PAINT_POSx, Settings.PAINT_POSy = newMapCorner
        self.labelMap.move(Settings.PAINT_POSx, Settings.PAINT_POSy)
        x1, y1 = self.labelMap.pos().x(), self.labelMap.pos().y()
        x2, y2 = x1 + self.pixmapMap.width(), y1 + self.pixmapMap.height()

        # Settings.POS_X = self.labelMap.pos().x()
        # Settings.POS_Y = self.labelMap.pos().y()

        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        koef = real_distance_map / lengh_meters

        # пересчитаем картинку и изменим ее
        width_new = self.pixmapMap.width() * koef
        height_new = self.pixmapMap.height() * koef

        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(
            self.pixmapMap.scaled(
                int(width_new),
                int(height_new),
                Qt.KeepAspectRatio,
                Qt.FastTransformation))
        # TODO может это красивое приближение и для False?
        #  Но - может возникать ошибка - self.ship_previous_pos
        #  может быть не определена при zoom. Так что подумать...
        if self.movingCentr == True:
            [Lat, Lon] = self.ship_previous_pos
            shipPos = self.getPointByCoordsCorner(Lat, Lon)
            x, y = shipPos
            self.moveLabelShip(int(x), int(y))


    # TODO: посмотреть self.ship_previous_pos передается ли всегда?
    def newGPScoordinates(self, Lat, Lon, rotate = 0):

        # сначала сделаем корабль видимым, безотносительно...
        if not self.labelShip.isVisible():
            self.labelShip.setVisible(True)

        # если двигаем КОРАБЛЬ, а не карту
        if self.movingCentr == False:

            # TODO: точка относительно УГЛА!!! НЕ используй
            #  getPointByCoords, перепиши другую!!!
            # self.getPointByCoordsCorner(Lat, Lon)
            # TODO: дерьмо в том, что при отключении "слежки" центр-то старый,
            #  и будет скачок координат. Ну или И центр менять при движении...

            newMapCorner = self.getPointByCoordsCorner(Lat, Lon)
            Settings.GPS_X, Settings.GPS_Y = newMapCorner
            self.moveLabelShip(int(Settings.GPS_X), int(Settings.GPS_Y), int(rotate))
        elif self.movingCentr == True:
            #с rotate придумать что-нить!
            if not self.ship_previous_pos:
                self.ship_previous_pos = [Lat, Lon]
                #print("first data ", Lat, Lon)
            else:
                prevPointX, prevPointY = self.getPointByCoordsCorner(self.ship_previous_pos[0], self.ship_previous_pos[1])
                curPointX, curPointY = self.getPointByCoordsCorner(Lat, Lon)
                prevPoint = QPoint(prevPointX, prevPointY)
                curPoint = QPoint(curPointX, curPointY)
                delta = prevPoint - curPoint
                #print('movingMap: ', Lat, Lon)
                newPos = self.labelMap.pos() + delta
                #Settings.POS_X, Settings.POS_Y = newPos.x(), newPos.y()
                self.labelMap.move(newPos)
                self.ship_previous_pos = [Lat, Lon]

    def moveLabelShip(self, x, y, rotate = 0):
        self.labelShip.moveLike(x, y, rotate)

    def updateScale(self, scale):
        Settings.CURRENT_MASHTAB = scale
        self.zoomMap()

    def createGrid(self):
        #Settings.NEED_GRID
        if self.labelGrid.isVisible() == False:
            self.labelGrid.setVisible(True)
            self.labelGrid.update()
        else:
            self.labelGrid.setVisible(False)
            self.labelGrid.update()

    # def updateSliderScale(self):
    #     Settings.CURRENT_MASHTAB = self.scale.value()
    #     scale_grid = Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]
    #     self.rescaleMap()


    def mouseDoubleClickEvent(self, event):

        # x_ground, y_ground, x_current, y_current
        point = self.getCoord(self.labelMap.pos().x(), self.labelMap.pos().y(),
                              event.pos().x(), event.pos().y())
        curLat1, curLon1 = point.split(', ')
        print('click! 1:', " .2: ", curLat1, curLon1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = event.pos()  # позиция Мыши
            self.label_old_pos = self.labelMap.pos() # позиция Карты
            self.ship_old_pos = self.labelShip.pos() # позиция корабля
        if event.button() == Qt.RightButton:
            print('center is: ', Settings.CENTR_LAT, ',', Settings.CENTR_LON, " set: ", Settings.BAUD_RATE, ' ', Settings.COM_PORT_EKHO)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = None
            self.doCentrPixels()
            if self.newCentr != '':
                Settings.CENTR_LAT, Settings.CENTR_LON = self.newCentr.split(', ')

    def mouseMoveEvent(self, event):
        # как только руками дернули - все, ушла настройка...
        self.movingCentr = False
        self.ship_previous_pos = []
        self.labelGrid.setModyfyed(True)
        self.labelGrid.update()

        if not self.mouse_old_pos:
            return
        # разница в передвижении:
        delta = event.pos() - self.mouse_old_pos
        self.mooving(delta)
        #self.update()

    # TODO: здесь, возможно, потребуется переопределить позиции мыши?...
    def mooving(self, delta, ship = 1):
        new_pos_label_map = self.label_old_pos + delta
        self.labelMap.move(new_pos_label_map)

        # после движения мышкой - обновим координаты угла
        # Settings.POS_X = new_pos_label_map.x()
        # Settings.POS_Y = new_pos_label_map.y()

        #пересчитаем координаты нового центра:
        new_pos_center = self.supposedCentr + delta
        self.newCentr = self.getCoordFromCentrPoint(new_pos_center.x(), new_pos_center.y(),
                                               int(Settings.DESCTOP_WIDHT / 2), int(Settings.DESCTOP_HEIGHT / 2))
        if(ship == 1):
            # пересчитаем корабль:
            new_pos_label_ship = self.ship_old_pos + delta
            self.labelShip.move(new_pos_label_ship)


class Login(QDialog):
    def __init__(self, parent=None):
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        print(Settings.DESCTOP_WIDHT, Settings.DESCTOP_HEIGHT)
        super(Login, self).__init__(parent)
        self.buttonLogin = QPushButton('Login', self)

        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QHBoxLayout(self)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        result = ['false', '', '']
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open image (.jpg, .png) file", "",
                                                  "JPEG(*.jpg *.jpeg);;PNG(*.png *.PNG);;All Files(*.*)",
                                                  options=options)
        # распарсим на ФАЙЛ и ПУТЬ
        filename = Path(fileName).name
        dir = Path(fileName).parent
        # распарсим ФАЙЛ на ИМЯ и РАСШИРЕНИЕ
        fileSourseName, fileSourseExtension = filename.split('.')
        KMLfile = None

        with os.scandir(dir) as files:
            for file in files:
                if file.is_file():
                    KMLfilename, KMLfile_extension = file.name.split('.')
                    if (KMLfile_extension.upper() == "KML") and (KMLfilename.upper() == fileSourseName.upper()):
                        KMLfile = KMLfilename + '.' + KMLfile_extension
        if (KMLfile != None):
            Settings.FILE_NAME = filename
            Settings.KML_FILE_NAME = KMLfile
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Chosen image file have not .kml file around!')


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.myWidget = Main()

        self.mainmenu = self.menuBar()
        # File ->
        self.menuFile = self.mainmenu.addMenu('File')
        # File -> Open
        self.menuOpen = self.menuFile.addMenu('Open...')
        # File -> Open -> Open Map File
        self.openMapFileAction = QAction(QIcon('icons/open.png'), 'Map File', self)
        self.openMapFileAction.triggered.connect(self.createGrid)
        self.menuOpenMap = self.menuOpen.addAction(self.openMapFileAction)
        # File -> Open -> Open Depth File
        self.menuOpenDepth = self.menuOpen.addAction('Depth File')
        # File.Connect
        self.comConnectAction = QAction(self)
        self.comConnectAction.setText('Connect...')
        self.comConnectAction.setIcon(QIcon('icons/com_port.png'))
        self.comConnectAction.setShortcut('Ctrl+C')
        self.comConnectAction.triggered.connect(self.waitingSerial)
        self.menuFile.addAction(self.comConnectAction)
        # File.Exit
        self.exitAction = QAction(QIcon('icons/exit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)
        self.menuFile.addAction(self.exitAction)


        # Settings ->
        self.menuSettings = self.mainmenu.addMenu('Settings')
        # Settings -> Add Grid
        self.menuGridAction = QAction(QIcon('icons/grid.png'), 'Add Grid', self)
        self.menuGridAction.triggered.connect(self.createGrid)
        self.menuGrid = self.menuSettings.addAction(self.menuGridAction)
        # Settings -> NMEA / COM
        self.menuNMEAAction = QAction(QIcon('icons/nmea.png'), 'NMEA/COM', self)
        self.menuNMEAAction.triggered.connect(self.openMNEAsettingsWindow)
        self.menuNMEA = self.menuSettings.addAction(self.menuNMEAAction)

        # self.toolbar = self.addToolBar('Exit')

        self.setCentralWidget(self.myWidget)

        self.statusBar = self.statusBar()
        strStatus = str(Settings().getGridScale()) + 'm, Grid=' + str(Settings().getScale())
        self.statusBar.showMessage(strStatus)

        self.scale = QSlider(self)
        self.scale.invertedControls()
        self.scale.setMinimum(1)
        self.scale.setMaximum(9)
        self.scale.setPageStep(1)
        self.scale.setSliderPosition(Settings().getScale())
        self.scale.setTickInterval(1)
        self.scale.setOrientation(QtCore.Qt.Vertical)
        self.scale.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.labelScale1 = QLabel(self)
        self.labelScale1.setText('1')
        self.labelScale1.setGeometry(int(Settings.DESCTOP_WIDHT - 45), int(Settings.DESCTOP_HEIGHT/2) + 120, 50, 50)
        self.labelScale9 = QLabel(self)
        self.labelScale9.setText('9')
        self.labelScale9.setGeometry(int(Settings.DESCTOP_WIDHT - 45), int(Settings.DESCTOP_HEIGHT/2) - 170 , 50, 50)
        self.labelScale5 = QLabel(self)
        self.labelScale5.setText('5')
        self.labelScale5.setGeometry(int(Settings.DESCTOP_WIDHT - 45), int(Settings.DESCTOP_HEIGHT/2) - 25, 50, 50)
        if Settings.DESCTOP_WIDHT is not None:
            self.scale.setGeometry(int(Settings.DESCTOP_WIDHT - 30), int(Settings.DESCTOP_HEIGHT/2) - 150, 25, 300)
        else:
            self.scale.setGeometry(1575, 320, 22, 300)
        self.scale.valueChanged.connect(self.updateScale)

        self.LCDspeed = QLCDNumber(self)
        self.LCDspeed.setStyleSheet("QLCDNumber { background-color: white; color: red; }")
        self.LCDspeed.setGeometry(5, 25, 110, 60)

        self.LCDcourse = QLCDNumber(self)
        self.LCDcourse.setStyleSheet("QLCDNumber { background-color: white; color: blue; }")
        self.LCDcourse.setGeometry(5, 85, 110, 60)

        self.LCDdepth = QLCDNumber(self)
        self.LCDdepth.setStyleSheet("QLCDNumber { background-color: white; color: black; }")
        self.LCDdepth.setGeometry(5, 145, 110, 60)

        self.LCDtime = QLCDNumber(self)
        self.LCDtime.setStyleSheet("QLCDNumber { background-color: white; color: black; }")
        self.LCDtime.setGeometry(5, 205, 110, 60)

        self.labelInfo = QLabel(self)
        self.labelInfo.setGeometry(5, 230, 210, 30)
        self.serial = QSerialPort(self)

        self.buttonKeep = QPushButton(self)
        self.buttonKeep.setGeometry(Settings.DESCTOP_WIDHT - 80, Settings.DESCTOP_HEIGHT - 80, 60, 60)
        self.buttonKeep.setIcon(QIcon('icons/target.png'))
        self.buttonKeep.setIconSize(QSize(55, 55))
        self.buttonKeep.clicked.connect(self.setCenterMoving)

        self.strData = ''
        self.dataStart = False
        self.keepCenter = False


    def updateScale(self):
        current_scale = self.scale.value()
        self.myWidget.updateScale(current_scale)
        strStatus = str(Settings().getGridScale()) + 'm, Grid=' + str(Settings().getScale())
        self.statusBar.showMessage(strStatus)

    def createGrid(self):
        self.myWidget.createGrid()

    def setCenterMoving(self):
        if self.keepCenter == False:
            self.keepCenter = True
            self.myWidget.setMovingCenter()
            self.buttonKeep.setIcon(QIcon('icons/target_ok.png'))
        else:
            self.buttonKeep.setIcon(QIcon('icons/target.png'))
            self.keepCenter = False
            self.myWidget.setMovingCenter()

    def openMNEAsettingsWindow(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
        dialog.show()

    def waitingSerial(self):
        try:
            if Settings.COM_PORT_EKHO is not None and (self.serial.isOpen() == False):
                self.serial.setPortName(Settings.COM_PORT_EKHO)
                self.serial.setBaudRate(int(Settings.BAUD_RATE))
                conn = self.serial.open(QIODevice.ReadOnly)
                if conn == True:
                    self.serial.readyRead.connect(self.onRead)
                    self.comConnectAction.setIcon(QIcon('icons/com_port_ok.png'))
                    self.comConnectAction.setText('Disconnect...')
            elif self.serial.isOpen() == True:
                self.serial.close()
                self.comConnectAction.setIcon(QIcon('icons/com_port.png'))
                self.comConnectAction.setText('Connect...')
        except Exception as e:
            print(e, ' waitingSerial')

    def onRead(self):
        buffer = ''
        try:
            buffer = self.serial.readLine()
        except Exception as e:
            print(e, ' onRead')
        rxs = str(buffer, 'utf-8')
        # если пришло всё в одной строке:
        try:
            if buffer != '':
                if "$" in rxs:
                    self.strData = ''
                    self.dataStart = True
                if self.dataStart == True:
                    self.strData = self.strData + rxs.strip()
                if (self.dataStart == True) and ("\r\n" in rxs):
                    self.dataStart == False
                    if len(self.strData) in range(20, 100):
                        if Settings.GPS_DEPTH_KEY in self.strData:
                            self.parsingDepthData(self.strData)
                        elif Settings.GPS_DATA_KEY in self.strData:
                            self.parsingGPSData(self.strData)
                    self.strData = ''
        except Exception as e:
            print(e, ' buffer ', self.strData)

    def parsingDepthData(self, str):
        data = str.split(',')
        strDepth = data[3]
        depth = float(strDepth)
        try:
            self.LCDdepth.display(depth)
        except Exception as e:
            print(e, ' parsingDepthData')

    def parsingGPSData(self, str):
        data = str.split(',')
        if data[2] == 'A':
            currentTime = data[1]
            tim = currentTime.split('.')
            time = tim[0]
            timeNorm = datetime.strptime(time, '%H%M%S') + timedelta(hours=3)
            self.LCDtime.display(timeNorm.strftime('%H:%M'))
            currentDate = data[9]
            course = int(data[8])
            Lat = data[3]
            LatSign = data[4]
            Lon = data[5]
            LonSign = data[6]
            strSpeed = data[7]
            speed = float(data[7]) * 1.85
            LatDEC = self.NMEA2decimal(Lat, LatSign)
            LonDEC = self.NMEA2decimal(Lon, LonSign)
            #print(LatDEC, LonDEC)
            if course in range(0, 360):
                self.LCDcourse.display(int(course))
            self.LCDspeed.display(speed)
            self.myWidget.newGPScoordinates(LatDEC, LonDEC, int(course))
        else:
            print("GPS coordinates are not valid yet. GPS sends", data[2], "value... Waiting...")

    def NMEA2decimal(self, strNMEA, sign):
        try:
            DD = int(float(strNMEA) / 100)
            SS = float(strNMEA) - DD * 100
            Dec = DD + SS / 60
            if (sign == "S") or (sign == "W"):
                return (0 - Dec)
            else:
                return Dec
        except Exception as e:
            print(e, ' NMEA2decimal ', strNMEA)


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setGeometry(0, 0, 420, 400)
        self.labelPort = QLabel(self)
        self.labelPort.setText('COM port:')
        self.labelPort.move(5, 20)
        self.comboPorts = QComboBox(self)
        self.comboPorts.move(70, 16)
        self.labelBaudRate = QLabel(self)
        self.labelBaudRate.setText('Baud rate:')
        self.labelBaudRate.move(5, 50)
        self.comboBaud = QComboBox(self)
        self.comboBaud.addItems(Settings.BAUD_RATES)
        self.comboBaud.move(70, 46)
        self.setCenter()
        self.ComPorts = self.setPorts()
        self.buttonOK = QPushButton(self)
        self.buttonOK.setText("OK")
        self.buttonOK.move(250, 350)
        self.buttonOK.clicked.connect(self.returnOK)
        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setText("Cancel")
        self.buttonNOT.move(330, 350)
        self.buttonNOT.clicked.connect(self.returnNOT)

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def setPorts(self):
        portList = []
        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            name = port.portName()
            descr = port.description()
            portList.append(name)
        self.comboPorts.addItems(portList)

    def returnOK(self):
        Settings.BAUD_RATE = self.comboBaud.currentText()
        Settings.COM_PORT_EKHO = self.comboPorts.currentText()
        self.accept()

    def returnNOT(self):
        self.close()



if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    login = Login()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = MainWindow()
        window.showFullScreen()
        sys.exit(app.exec_())