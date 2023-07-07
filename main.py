#!/usr/bin/python3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QFileDialog, QLabel, QWidget, QMainWindow, QApplication, QSlider, \
    QAction, qApp, QToolBar, QStackedWidget, QPushButton, QDesktopWidget, QComboBox, QCheckBox, \
    QTextEdit, QTextBrowser, QStackedLayout, QColorDialog, QMenu, QToolButton, QVBoxLayout, QGroupBox, QGridLayout, \
    QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsSimpleTextItem, QGraphicsTextItem, QLineEdit, QSpacerItem
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
from PyQt5.QtCore import Qt, QPoint, QRect, QIODevice, QSize, QPointF, QSettings, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon, QFont, QImage, QBrush
from PyQt5.Qt import QTransform, QStyle, QStyleOptionTitleBar, QSizePolicy
from datetime import *
from PyQt5.QtCore import QTime, QTimer, QDateTime
import time

############
import pandas as pd
import numpy as np
from numpy import arange
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib import rcParams, colors
from math import cos, radians, ceil
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.figure import Figure
import scipy.interpolate as si
#############
import stylescss
import stylescss as styles
from PIL import Image, ImageOps, ImageFilter
from PIL.ImageQt import ImageQt
import sqlite3

from PyQt5.QtGui import QCursor


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
    NEED_FISHING_CIRCLE = False
    NEED_RADIUS_VECTOR = False
    NEED_RADIUS_TEXT = True
    FISHING_SIRCLE_RADIUS = 60
    FISHING_SIRCLE_QNT = 2
    CIRCLE_COLOR = None
    MASHTAB_MIN = 1
    MASHTAB_MAX = 9
    FILE_NAME = None  # "OKA_19_160.jpg"
    KML_FILE_NAME = None
    FILE_DEPTH_NAME = None  # "djer.csv"
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
    PLOT_PALETTE = {"Base": ["#990000", "#cc0000", "#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ccff33", "#99ff66",
                            "#66ff99", "#33ffcc", "#00ffff", "#00ccff", "#0099ff", "#0066ff", "#0033ff", "#0000ff", "#0000cc", "#000099"],
                    "Bright": ["#cc7f7f", "#e57f7f", "#ff7f7f", "#ff997f", "#ffb27f", "#ffcc7f", "#ffcc7f", "#ffff7f", "#e5ff99",
                               "#ccffb2", "#b2ffcc", "#99ffe5", "#7fffff", "#7fe5ff", "#7fccff", "#7fb2ff", "#7f99ff", "#7f7fff", "#7f7fe5", "#7f7fcc"],
                    "Water": ["#A9D6E5", "#89C2D9", "#61A5C2", "#468FAF", "#2C7DA0", "#2A6F97", "#014F86", "#01497C", "#013A63", "#012A4A", "#01243E"],
                    "Test": ["#e73b0a", "#d64d0f", "#d1631d", "#d48936", "#594c2e", "#5f5a48", "#3a413a", "#656856", "#6d7e72"],
                    "Zhura": ["#ba1505", "#fa9411", "#f6c318", "#ecd410", "#d7cc13",
                              "#b9bf14", "#85c42b", "#13a933", "#05ab58", "#069765", "#167377", "#20577f", "#152a7a", "#0e125b"
                              ],
                    "WaterDeep": ["#ffffff", "#e6f2fd", "#cce5fb", "#b3d8fa", "#99cbf8", "#80bff7", "#66b2f5", "#4da5f3", "#3398f2", "#1a8cf0", "#007fef",
                                  "#0274d9", "#046ac5", "#065fae", "#08569a", "#0a4b85", "#0c4070", "#0e365b", "#102c45", "#122230", "#14181c"
                                  ]
                    }
    CURRENT_PALETTE = "Base"
    DEBUG_INFO = False
    ALPHA_CONTOUR = 1
    ALPHA_CONTOURS = ["1", "0.75", "0.5", "0.25"]
    FREQUENCIES_LINES = ["1", "0.5", "0.25"]
    DEPTH_LINES  = ["1", "0.5", "0.25"]
    CURRENT_FREQUENCY_LINES = 1
    BASE_NMEA = {'comport': 'COM1', 'baudrate': '9600'}
    HEIGHT_SCREEN = None
    WIDTH_SCREEN = None



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
        path = self.getPath()
        self.setScaledContents(True)
        path_ship = os.path.join(path, 'icons', 'lodka_med.png')
        self.pix = QPixmap(path_ship)
        self.setPixmap(self.pix)

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path


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

    def rotation(self, angel = 0):
        if angel:
            t = QTransform().rotate(angel)
            self.setPixmap(self.pix.transformed(t))

# постоянный Paint event
class LabelGrid(QLabel):

    # TODO: обрабатывать событие ухода с экрана - через self.label.update()
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setGeometry(0, 0, Settings.DESCTOP_WIDHT, Settings.DESCTOP_HEIGHT)
        self.IsModyfied = True
        self.moving = QPoint()
        self.posLabelMap = QPoint(Settings.POS_X, Settings.POS_Y)
        self.lastX = self.posLabelMap.x()
        self.lastY = self.posLabelMap.y()

    def paintEvent(self, event):
        if self.IsModyfied == True:
            super().paintEvent(event)
            currentPosition = self.posLabelMap
            print("grid grid", currentPosition, self.posLabelMap, self.lastX)
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

    def setCurrentMapPosition(self, position):
        self.posLabelMap = position


class WhiteBack(QWidget):
    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: white;')


class MapGrid(QWidget):
    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)

        # Объект - Label с наложенной сеткой
        self.labelGrid = LabelGrid(self)
        self.labelGrid.setVisible(False)

    def proxyToGridPosition(self, position):
        self.labelGrid.setCurrentMapPosition(position)

    def move_grid_on(self):
        self.labelGrid.setModyfyed(True)

    def move_grid_off(self):
        self.labelGrid.setModyfyed(False)

    def zoom_grid(self):
        self.labelGrid.update()
        self.labelGrid.setModyfyed(True)

    def createGrid(self):
        #Settings.NEED_GRID
        if self.labelGrid.isVisible() == False:
            self.labelGrid.setVisible(True)
            self.labelGrid.update()
        else:
            self.labelGrid.setVisible(False)
            self.labelGrid.update()

    def labelGridUpdate(self):
        self.labelGrid.update()


class LabelMapShip(QWidget):
    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)
        self.labelShip = LabelShip(self)
        self.labelShip.setVisible(False)
        self.old_pos = None

    def setShipOldPos(self):
        self.old_pos = self.labelShip.pos()

    def moveLabelShip(self, x, y, rotate = 0):
        if not self.labelShip.isVisible():
            self.labelShip.setVisible(True)
        self.labelShip.moveLike(x, y, rotate)

    def clearLabelShip(self):
        if self.labelShip.isVisible():
            self.labelShip.setVisible(False)

    def mooving(self, delta):
        if self.labelShip.isVisible():
            new_pos_label_ship = self.old_pos + delta
            self.labelShip.move(new_pos_label_ship)

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
                self.labelShip.rotation(int(rotate))
                Settings.POS_X, Settings.POS_Y = newPos.x(), newPos.y()
                self.labelMap.move(newPos)
                self.ship_previous_pos = [Lat, Lon]


class GridWidget(QWidget):
    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)
        self.IsModyfied = True
        self.posLabelMap = QPoint(Settings.POS_X, Settings.POS_Y)
        self.lastX = self.posLabelMap.x()
        self.lastY = self.posLabelMap.y()
        self.mPixmap = QPixmap()
        self.setVisible(False)


    def paintEvent(self, event):
        self.window_height = self.size().height()
        self.window_width = self.size().width()
        if self.IsModyfied == True:
            pixmap = QPixmap(self.size())
            pixmap.fill(QColor(0, 0, 0, 0))
            currentPosition = self.posLabelMap
            dx = 0
            dy = 0
            painter = QPainter(pixmap)
            if (self.lastX != currentPosition.x()) or (self.lastY != currentPosition.y()):
                dx = self.lastX - currentPosition.x()
                dy = self.lastY - currentPosition.y()
            x = int(self.window_width / 2) - dx
            y = int(self.window_height / 2) - dy
            qntX = int(self.window_width / Settings.GRID_STEP)
            qntY = int(self.window_height / Settings.GRID_STEP)
            # TODO: теперь сюда нужно посчитать смещение, прибавить по X и Y!
            # докрутить!
            for i in range(int(self.window_width / qntX), self.window_width + abs(dx), Settings.GRID_STEP):
                painter.drawLine(x, 0, x, self.window_height)
                painter.drawLine(x + i, 0, x + i, self.window_height)
                painter.drawLine(x - i, 0, x - i, self.window_height)
            for i in range(int(self.window_height / qntY), self.window_height + abs(dy), Settings.GRID_STEP):
                painter.drawLine(0, y, self.window_width, y)
                painter.drawLine(0, y + i, self.window_width, y + i)
                painter.drawLine(0, y - i, self.window_width, y - i)
            self.mPixmap = pixmap
            self.IsModyfied = False

        qp = QPainter(self)
        qp.drawPixmap(0, 0, self.mPixmap)

    def setCurrentMapPosition(self, position):
        self.posLabelMap = position

    def setModyfyed(self):
        self.IsModyfied = True

    def zoom_grid(self):
        self.update()
        self.setModyfyed()

    def createGrid(self):
        #Settings.NEED_GRID
        if self.isVisible() == False:
            self.setVisible(True)
            self.update()
        else:
            self.setVisible(False)
            self.update()

# TODO - visible завязать еще с ship
class Circles(QWidget):
    def __init__(self):
        super().__init__()
        #super().__init__()
        self.screen_width = Settings.WIDTH_SCREEN
        self.screen_height = Settings.HEIGHT_SCREEN
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.shipPosition = QPointF()
        self.shipPosition.setX(Settings.POS_SHIP_X)
        self.shipPosition.setY(Settings.POS_SHIP_Y)
        self.setVisible(False)
        self.course = 0
        self.actionPoint = QPointF()
        self.circleVisible = False

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.circleVisible:
            if Settings.CIRCLE_COLOR is not None:
                color_pen = QColor()
                color_pen.setNamedColor(Settings.CIRCLE_COLOR)
                pen = QPen(color_pen, 2, Qt.PenStyle.SolidLine)
            else:
                pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing)
            for qnt in range(1, Settings.FISHING_SIRCLE_QNT + 1):
                rad = qnt * ((Settings.GRID_STEP * Settings.FISHING_SIRCLE_RADIUS) / \
                      int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])) / Settings.FISHING_SIRCLE_QNT
                painter.drawEllipse(self.shipPosition, rad, rad)
                if Settings.NEED_RADIUS_TEXT:
                    realRadius = Settings.FISHING_SIRCLE_RADIUS / (Settings.FISHING_SIRCLE_QNT + 1 - qnt)
                    textPos = QPointF()
                    text = str(round(realRadius, 1)) + ' m'
                    textPos.setX(self.shipPosition.x() - len(text))
                    textPos.setY(self.shipPosition.y()  - rad - 2)
                    painter.drawText(textPos, text)

        if Settings.NEED_RADIUS_VECTOR:
            max_rad = (Settings.GRID_STEP * Settings.FISHING_SIRCLE_RADIUS) / int(
                     Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
            radiansCourse = radians(self.course)
            degresCource = degrees(radiansCourse) + 90
            rightCourse = radians(degresCource)

            radius_point_x = self.shipPosition.x() - max_rad*cos(rightCourse)
            radius_point_y = self.shipPosition.y() - max_rad*sin(rightCourse)
            point_1 = QPointF(self.shipPosition.x(), self.shipPosition.y())
            point_2 = QPointF(radius_point_x, radius_point_y)
            painter.drawLine(point_1, point_2)

        if self.actionPoint:
            #TODO добавить из серии, if coords in (scr_w, scr_h)
            lines_pen = QPen(Qt.darkGray, 1, Qt.PenStyle.DashLine)
            x_point, y_point = self.actionPoint.x(), self.actionPoint.y()
            painter.setPen(lines_pen)
            painter.drawLine(0, y_point, self.screen_width, y_point)
            painter.drawLine(x_point, 0, x_point, self.screen_height)
            white_width = 3
            white_height = 12
            black_pen = QPen(Qt.black, 2, Qt.PenStyle.SolidLine)
            painter.setPen(black_pen)
            painter.drawLine(x_point - white_height, y_point - white_width, x_point + white_height, y_point - white_width)
            painter.drawLine(x_point - white_height, y_point + white_width, x_point + white_height, y_point + white_width)
            painter.drawLine(x_point - white_width, y_point + white_height, x_point - white_width, y_point - white_height)
            painter.drawLine(x_point + white_width, y_point + white_height, x_point + white_width, y_point - white_height)
            white_pen = QPen(Qt.white, white_width, Qt.PenStyle.SolidLine)
            painter.setPen(white_pen)
            painter.drawLine(x_point - white_height, y_point, x_point + white_height, y_point)
            painter.drawLine(x_point, y_point - white_height, x_point, y_point + white_height)

    def setPointToAction(self, point=None, visible=None):
        result = False
        if visible == False:
            self.actionPoint.setX()
            self.actionPoint.setY()

        if point is not None:
            result = True

        self.actionPoint = point
        print("get!", self.actionPoint)
        self.update()
        return result

    def setShipPosition(self, x, y, rotation = 0):
        self.shipPosition.setX(x)
        self.shipPosition.setY(y)
        self.course = rotation
        self.update()

    def checkVisible(self):
        if Settings.NEED_FISHING_CIRCLE == False:
            self.setVisible(False)
            self.circleVisible = False
            self.update()
        else:
            self.setVisible(True)
            self.circleVisible = True
            self.update()

    def setVisibleLine(self, visible):
        self.setVisible(visible)
        self.update()


class MyQLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, e):
        print("ZALUPA!")
        self.clicked.emit()


class FishIconsClass(QWidget):
    def __init__(self):
        super().__init__()
        self.path = self.getPath()
        path_images = os.path.join(self.path, 'icons', 'fishIcons.png')
        self.pixmap_icons = QPixmap(path_images)

        self.screen_width = Settings.WIDTH_SCREEN
        self.screen_height = Settings.HEIGHT_SCREEN
        self.reqt_screen = QRect(0, 0, self.screen_width, self.screen_height)
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.iconsVisible = False
        self.connection = self.initConnect()
        #self.selectPoints(self.connection)
        self.coords_list = None
        self.labels_old_pos = {}

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path

    def initConnect(self):
        if not os.path.exists('db'):
            os.makedirs('db')
        #TODO - path!!!
        path = os.path.join(os.getcwd(), 'db', 'main_db.db')
        connection = sqlite3.connect(path)
        return connection

    def selectPoints(self, conn):
        sqlite_select_query = "SELECT * from map_points"
        cursor = conn.cursor()
        cursor.execute(sqlite_select_query)
        self.coords_list = cursor.fetchall()
        cursor.close()

    def getCoordsAndIcons(self, list_data):
        labels_names = []
        for label_one in self.findChildren(QLabel):
            labels_names.append(label_one.objectName())
        # (908, 525, '1_3', 'test', '2023-07-06_00-44-35')
        if list_data is not None:
            for data in list_data:
                point = QPoint(data[0], data[1])
                y, x = data[2].split('_')
                req = QRect(QPoint(int(x) * 22, int(y) * 22), QPoint(int(x) * 22 + 21, int(y) * 22 + 21))
                pix = self.pixmap_icons.copy(req)
                label_name = data[4]

                new_point = QPoint()
                new_point.setX(point.x() - 11)
                new_point.setY(point.y() - 11)

                label_find = self.findChild(QLabel, label_name)

                if label_find:
                    self.labels_old_pos[label_find.objectName()] = new_point
                    if self.reqt_screen.contains(new_point):
                        label_find.move(new_point)
                        if not label_find.isVisible():
                            label_find.setVisible(True)
                    else:
                        label_find.move(new_point)
                        if label_find.isVisible():
                            label_find.setVisible(False)
                else:
                    label = MyQLabel(self)
                    label.clicked.connect(self.clickLabel)
                    label.setObjectName(label_name)
                    self.labels_old_pos[label_name] = new_point
                    label.setPixmap(pix)
                    label.move(new_point)
                    if not self.reqt_screen.contains(new_point):
                        label.setVisible(False)
        self.update()

    def clickLabel(self):
        print("label.objectName()")


    def setIconsOldPos(self):
        for label in self.findChildren(QLabel):
            if label.objectName() in self.labels_old_pos:
                self.labels_old_pos[label.objectName()] = label.pos()

    def moveIcons(self, delta):
        for label in self.findChildren(QLabel):
            if label.objectName() in self.labels_old_pos:
                label_new_pos = self.labels_old_pos[label.objectName()] + delta
                label.move(label_new_pos)
                if not self.reqt_screen.contains(label_new_pos):
                    label.setVisible(False)
                else:
                    label.setVisible(True)


class Main(QWidget):
    mouse_old_pos = None
    label_old_pos = None
    label_pillow_old_pos = None
    # для передвижения вместе с картой при тапе
    ship_old_pos = None
    old_pos = None
    mashtab = Settings.CURRENT_MASHTAB
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
        #тут хранятся ТЕКУЩИЕ центральные координаты
        self.newCentr = ''
        self.setGeometry(0, 0, screen_width, screen_height)
        # в самом начале установим координаты центральной точки в 0 - 0
        Settings.CENTR_LAT = 0
        Settings.CENTR_LON = 0
        self.posX = None
        self.posY = None
        self.supposedCentr = QPointF()
        self.doCentrPixels()
        # Получим список координат
        self.labelMap = QLabel(self)
        self.labelMap.move(350, 210)
        self.updateCentrPoint()

        self.source_image_width = None
        self.source_image_height = None

        self.addImage()

        #########
        ######### TODO - убери это!!! border = 5 для анализа поставь!
        self.screen_old_pos = QPointF(screen_width/2, screen_height/2)
        self.labelPillowMap = QLabel(self)
        self.labelPillowMap.setStyleSheet('border-style: solid; border-width: 0px; border-color: green;')
        self.labelPillowMap.move(350, 210)
        #self.addImagePillow()
        #########
        #########

        # включим отслеживание мышки
        #self.setMouseTracking(True)

        self.labelShip = LabelShip(self)
        self.labelShip.setVisible(False)

        self.movingCentr = False
        self.centrPoint = QPoint()
        self.centrPoint.setX(int(Settings.DESCTOP_WIDHT / 2))
        self.centrPoint.setY(int(Settings.DESCTOP_HEIGHT / 2))


        # Определим РЕАЛЬНОЕ (по координатам) расстояние между точками из KML
        # И отобразим на карте!
        # TODO : возможно, ресайзить нужно backgroung...

    def resetAfterNewImage(self):
        Settings.CENTR_LAT = 0
        Settings.CENTR_LON = 0
        self.supposedCentr = QPoint()
        self.doCentrPixels()

    def mousePressEvent(self, event):
        print("position global widget = ", event.globalPos())

    def setMovingCenter(self):
        if self.movingCentr == True:
            self.movingCentr = False
            self.ship_previous_pos = []
        else:
            self.movingCentr = True

    def makeMovingCenterFalse(self):
        self.movingCentr = False

    def setPrevShipPodNone(self):
        self.ship_previous_pos = []

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

    def getNewCenter(self):
        return self.newCentr

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
    def addImage(self, fromParent = False):
        # первоначальное добавление картинки
        if fromParent:
            self.resetAfterNewImage()


        self.pixmapMap = QPixmap(Settings.FILE_NAME)
        self.source_image_width = self.pixmapMap.width()
        self.source_image_height = self.pixmapMap.height()

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
        self.koef = real_distance_map / lengh_meters
        width_new = self.pixmapMap.width() * self.koef
        height_new = self.pixmapMap.height() * self.koef


        # TODO: сделать добавление, чтобы по координатам был (в центре экрана - нужная координата)
        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(self.pixmapMap.scaled(int(width_new), int(height_new), Qt.KeepAspectRatio, Qt.FastTransformation))


    def addImagePillow(self):
        self.rect_screen = QRect(0, #-Settings.DESCTOP_WIDHT,
                                 0, #-app.primaryScreen().size().height(),
                                 Settings.DESCTOP_WIDHT,
                                 (app.primaryScreen().size().height()))
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        # первоначальное добавление картинки
        self.pillImage = Image.open(Settings.FILE_NAME)
        self.picture_width, self.picture_height = self.pillImage.size
        print("self.picture_width, self.picture_height", self.picture_width, self.picture_height)
        self.big_diagonal = ( (screen_width ** 2) + (screen_height ** 2) ) ** (0.5)
        print("self.big_diagonal", self.big_diagonal)
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
        x2, y2 = x1 + self.picture_width, y1 + self.picture_height
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        self.koef = real_distance_map / lengh_meters
        width_new = self.picture_width * self.koef
        height_new = self.picture_height * self.koef

        # TODO: сделать добавление, чтобы по координатам был (в центре экрана - нужная координата)
        self.labelMap.resize(int(width_new), int(height_new))
        print("self.labelMap.", self.labelMap.size(), self.koef)
        self.pillowLabelSetImage(first_set=True)

    def pillowLabelSetImage(self, first_set=False):

        print(self.supposedCentr)

        # TODO: строить нужно с запасом!
        # тогда когда мы делаем move - мы просто move label, а при остановке -
        # отрисовываем в Pixmap
        # пересечение экрана rect_screen и label_map в текущей позиции
        # для фиксации размера labelPillowMap
        #rect_screen = QRect(0, 0, Settings.DESCTOP_WIDHT, app.primaryScreen().size().height())
        #rect_screen = QRect(0-Settings.DESCTOP_WIDHT, 0-app.primaryScreen().size().height(), 3*Settings.DESCTOP_WIDHT, 3*(app.primaryScreen().size().height()))
        #rect_screen = QRect(0, 0, Settings.DESCTOP_WIDHT, (app.primaryScreen().size().height()))

        label_map_rect = QRect(self.labelMap.pos(), self.labelMap.size())
        label_pillow_reqt = QRect(self.labelPillowMap.pos(), self.labelPillowMap.size())

        #cross_reqt = rect_screen.intersected(label_map_rect)
        cross_reqt = label_map_rect.intersected(self.rect_screen)
        cross_reqt_size = cross_reqt.getRect()
        print(first_set,
              "cross_reqt", cross_reqt, #cross_reqt_size,
              "rect_screen", self.rect_screen,
              "label_pillow_reqt", label_pillow_reqt,
              "label_map_rect", label_map_rect)
        self.labelPillowMap.setGeometry(cross_reqt)
        self.labelPillowMap.setAlignment(QtCore.Qt.AlignLeft)

        if cross_reqt != QRect(0, 0, 0, 0):
            if (cross_reqt != label_map_rect) or first_set:

                #print("labelMap", self.labelMap.pos(), self.labelMap.size())
                width_new = int(self.picture_width * self.koef)
                height_new = int(self.picture_height * self.koef)

                pillImage_current = self.pillImage.resize((int(width_new), int(height_new)))

                crop_list = (cross_reqt_size[0] - self.labelMap.pos().x(),
                             cross_reqt_size[1] - self.labelMap.pos().y(),
                             (cross_reqt_size[0] - self.labelMap.pos().x()) + cross_reqt_size[2],
                             (cross_reqt_size[1] - self.labelMap.pos().y()) + cross_reqt_size[3]
                             )
                print("crop_list:", crop_list)
                im = pillImage_current.crop(crop_list)
                im = im.convert("RGBA")
                qim = ImageQt(im)
                pixmap = QPixmap(QImage(qim))
                self.labelPillowMap.setPixmap(pixmap)


    def getLabelMapPosition(self):
        return self.labelMap.pos()

    # увеличение / уменьшение картинки
    # TODO: возможно, добавить и смещение - отдельной функцией.
    def zoomMap(self):

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

        # Нужно для grid
        Settings.POS_X = self.labelMap.pos().x()
        Settings.POS_Y = self.labelMap.pos().y()

        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        self.koef = real_distance_map / lengh_meters

        # пересчитаем картинку и изменим ее
        width_new = self.pixmapMap.width() * self.koef
        height_new = self.pixmapMap.height() * self.koef

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
                self.labelShip.rotation(int(rotate))
                #Settings.POS_X, Settings.POS_Y = newPos.x(), newPos.y()
                self.labelMap.move(newPos)
                self.ship_previous_pos = [Lat, Lon]

    def moveLabelShip(self, x, y, rotate = 0):
        self.labelShip.moveLike(x, y, rotate)

    def updateScale(self, scale):
        Settings.CURRENT_MASHTAB = scale
        self.zoomMap()

    def setLabelOldPos(self, pos):
        self.label_old_pos = pos

    def setScreenOldPos(self, pos):
        self.screen_old_pos = pos

    def setLabelPillowOldPos(self, pos):
        self.label_pillow_old_pos = pos

    # TODO: здесь, возможно, потребуется переопределить позиции мыши?...
    def mooving(self, delta):
        new_pos_label_map = self.label_old_pos + delta
        self.labelMap.move(new_pos_label_map)

        # после движения мышкой - обновим координаты угла
        Settings.POS_X = new_pos_label_map.x()
        Settings.POS_Y = new_pos_label_map.y()

        #пересчитаем координаты нового центра:
        new_pos_center = self.supposedCentr + delta
        self.newCentr = self.getCoordFromCentrPoint(new_pos_center.x(), new_pos_center.y(),
                                               int(Settings.DESCTOP_WIDHT / 2), int(Settings.DESCTOP_HEIGHT / 2))

        new_pos_label_pillow = self.label_pillow_old_pos + delta
        self.labelPillowMap.move(new_pos_label_map)


        #self.test_moving()

    def test_moving(self):

        rect_screen = QRect(0, 0, Settings.DESCTOP_WIDHT, app.primaryScreen().size().height())
        label_map_width = self.labelMap.size().width()
        label_map_height = self.labelMap.size().height()

        label_map_rect = QRect(self.labelMap.pos(), self.labelMap.size())
        cross_reqt = label_map_rect.intersected(rect_screen)

        dy = (self.labelMap.pos().y() - cross_reqt.getRect()[1])
        dx = (self.labelMap.pos().x() - cross_reqt.getRect()[0])

        #coeffizient =

        self.labelPillowMap.setGeometry(cross_reqt)


        crop_source = (

            int(abs(dx)/self.koef),
            int(abs(dy)/self.koef),
            int((abs(dx)/self.koef) + cross_reqt.getRect()[2]/self.koef),
            int((abs(dy)/self.koef) + cross_reqt.getRect()[3]/self.koef),
        )

        print("cross_reqt", cross_reqt.getRect(), dx, dy, self.source_image_width, self.source_image_height, self.koef, crop_source)


    def getCurrentLabelMapPos(self):
        return self.labelMap.pos()

    def getCurrentLabelPillowPos(self):
        return self.labelPillowMap.pos()

    def getCurrentScreenCenter(self):
        return self.rect_screen.center()

    def getCurrentLabelShipPos(self):
        return self.labelShip.pos()


class Login(QDialog):
    def __init__(self, parent=None):
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        print(Settings.DESCTOP_WIDHT, Settings.DESCTOP_HEIGHT)
        super(Login, self).__init__(parent)
        path = self.getPath()
        self.setWindowTitle("Image Map")
        self.setFixedWidth(290)
        self.setFixedHeight(400)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: white;')
        path_map = os.path.join(path, 'icons', 'map.png')
        self.buttonLogin = QPushButton('', self)
        #self.buttonLogin.setIcon(QIcon('icons/map.png'))
        self.buttonLogin.setIcon(QIcon(path_map))
        self.buttonLogin.setIconSize(QSize(114, 162))
        self.buttonLogin.setFixedSize(114, 162)
        self.buttonLogin.clicked.connect(self.handleLogin)

        self.buttonGPS = QPushButton('', self)
        path_gps = os.path.join(path, 'icons', 'gps.jpg')
        #self.buttonGPS.setIcon(QIcon('icons/gps.jpg'))
        self.buttonGPS.setIcon(QIcon(path_gps))
        self.buttonGPS.setIconSize(QSize(114, 162))
        self.buttonGPS.setFixedSize(114, 162)
        self.buttonGPS.clicked.connect(self.startGPS)

        #self.labelChose = QLabel(self)
        #self.labelChose.setGeometry(0, -100, 250, 300)
        #self.labelChose.setText(path_map)
        layout = QHBoxLayout(self)
        layout.addWidget(self.buttonLogin)
        layout.addWidget(self.buttonGPS)

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path


    def startGPS(self):
        pass

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

        if (KMLfile is not None):
            Settings.FILE_NAME = fileName #filename
            Settings.KML_FILE_NAME = os.path.join(dir, KMLfile) #KMLfile
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Chosen image file have not .kml file around!')


class MainWindow(QMainWindow):

    mouse_old_pos = None
    label_old_pos = None
    # для передвижения вместе с картой при тапе
    ship_old_pos = None
    coordsNW = None
    coordsNE = None
    coordsSW = None
    coordsSE = None
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.path = self.getPath()
        self.initSettings()
        self.main_window_height = app.primaryScreen().size().height()
        self.main_window_width = app.primaryScreen().size().width()
        Settings.HEIGHT_SCREEN = self.main_window_height
        Settings.WIDTH_SCREEN = self.main_window_width
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.myWidget = Main()
        self.gridWidget = MapGrid()
        self.shipWidget = LabelMapShip()
        self.gridW = GridWidget()
        self.circles = Circles()
        self.whiteBack = WhiteBack()
        self.iconsWidget = FishIconsClass()
        self.currentPointToSave = QPointF()
        #####
        self.figure = plt.figure(clear=True)
        self.figure.set_alpha(0)
        self.figure.patch.set_facecolor("None")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color:transparent;")
        if Settings.FILE_DEPTH_NAME is not None and self.coordsNW is not None:
            self.plot()
        #####

        layout = QStackedLayout()
        layout.setStackingMode(QStackedLayout.StackAll)

        layout.addWidget(self.whiteBack)
        layout.addWidget(self.myWidget)
        layout.addWidget(self.canvas)
        layout.addWidget(self.gridW)
        layout.addWidget(self.iconsWidget)
        layout.addWidget(self.shipWidget)
        layout.addWidget(self.circles)

        widget = QWidget()
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.baseLCDy = 60

        shadow = QtWidgets.QGraphicsDropShadowEffect(self,
            blurRadius=14.0,
            color = QColor("white"),
            offset = QtCore.QPointF(0.0, 0.0))

        self.labelLetterDepth = QLabel(self)
        self.labelLetterDepth.setGeometry(12, 20, 120, 20)
        self.labelLetterDepth.setText("DEPTH, M") #    M
        self.labelLetterDepth.setStyleSheet(styles.labelLetterDepth)
        self.labelLetterDepth.setGraphicsEffect(shadow)

        self.labelDepth = QLabel(self)
        self.labelDepth.setGeometry(20, 50, 150, 50)
        self.labelDepth.setText("-.-")
        self.labelDepth.setStyleSheet(styles.labelDepth)
        self.labelDepth.setGraphicsEffect(shadow)



        '''
        self.scene = QGraphicsScene()
        graphView = QGraphicsView(self.scene, self)
        graphView.setGeometry(0, 120, 150, 170)
        self.qText = QGraphicsSimpleTextItem()
        self.qText.setText("-.-")
        self.qText.boundingRect()
        font = QFont('Arial', pointSize=55)
        font.setBold(True)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColor(168, 34, 3))
        pen = QPen()
        pen.setColor(QColor(0, 0, 0))
        self.qText.setBrush(brush)
        self.qText.setPen(pen)
        self.qText.setFont(font)
        self.scene.addItem(self.qText)
        '''

        self.serial = QSerialPort(self)


        self.buton_size = 40
        self.buttonZoomMinus = QPushButton(self)
        self.buttonZoomMinus.setGeometry(int(self.main_window_width/2),
                                        int(self.main_window_height) - self.buton_size,
                                        self.buton_size,
                                        self.buton_size)
        self.buttonZoomMinus.setText("-")
        self.buttonZoomMinus.setStyleSheet(styles.buttonZOOMminus)
        self.buttonZoomMinus.clicked.connect(self.zoomMinus)

        self.buttonZoomPlus = QPushButton(self)
        self.buttonZoomPlus.setGeometry(int(self.main_window_width/2 - self.buton_size),
                                        int(self.main_window_height) - self.buton_size,
                                        self.buton_size,
                                        self.buton_size)
        self.buttonZoomPlus.setText("+")
        self.buttonZoomPlus.setStyleSheet(styles.buttonZOOMplus)
        self.buttonZoomPlus.clicked.connect(self.zoomPlus)

        self.lineEditDebug = QTextBrowser(self)
        self.lineEditDebug.setGeometry(5, self.baseLCDy + 241, 250, 120)
        self.lineEditDebug.setVisible(False)

        self.strData = ''
        self.dataStart = False
        self.keepCenter = False

        menu_button_width = 140

        self.menu = QMenu(self)
        self.menu.setFixedWidth(menu_button_width)
        self.menu.setStyleSheet(styles.menuStyle)

        self.subMenuSettings = self.menu.addMenu('Settings')
        self.settingsNMEAAction = QAction('NMEA', self)
        self.settingsNMEAAction.triggered.connect(self.openMNEAsettingsWindow)
        self.subMenuSettings.addAction(self.settingsNMEAAction)
        self.settingsMapsAction = QAction('Map', self)
        self.settingsMapsAction.triggered.connect(self.openMAPsettingsWindow)
        self.subMenuSettings.addAction(self.settingsMapsAction)

        self.subMenuMaps = self.menu.addMenu('Open map')
        self.depthMapAction = QAction('Depth', self)
        self.depthMapAction.triggered.connect(self.getDepthMapFile)
        self.subMenuMaps.addAction(self.depthMapAction)
        self.backgroundMapAction = QAction('Image', self)
        self.backgroundMapAction.triggered.connect(self.addImageDialog)
        self.subMenuMaps.addAction(self.backgroundMapAction)

        self.connectAction = QAction('Connect', self)
        self.connectAction.setObjectName("connect")
        self.connectAction.triggered.connect(self.waitingSerial)
        self.menu.addAction(self.connectAction)

        self.addGridAction = QAction('Add Grid', self)
        self.addGridAction.triggered.connect(self.createGrid)
        self.menu.addAction(self.addGridAction)

        self.addLogAction = QAction('Write Log', self)
        self.addLogAction.triggered.connect(self.writeLogs)
        self.menu.addAction(self.addLogAction)

        self.addScrshotAction = QAction('Screenshot', self)
        self.addScrshotAction.triggered.connect(self.screenShot)
        self.menu.addAction(self.addScrshotAction)

        ##### EXIT #####
        self.exitAction = QAction('Exit', self)
        self.exitAction.triggered.connect(qApp.quit)
        self.menu.addAction(self.exitAction)

        self.button = QToolButton(self)
        self.button.setMenu(self.menu)
        self.button.setPopupMode(QToolButton.InstantPopup)
        self.button.setText('Menu')
        self.button.setGeometry(int(self.main_window_width - menu_button_width), 0, menu_button_width, 60)
        self.button.setStyleSheet(styles.menuButtonStyle)

        self.current_scale = Settings.CURRENT_MASHTAB
        self.ship_speed = 0.0

        lblInfoH = 30
        lblInfoW = 190
        #        self.main_window_width
        #        self.main_window_height

        self.labelInfoSOG = QLabel(self)
        self.labelInfoSOG.setStyleSheet(styles.labelInfoTop)
        self.labelInfoSOG.setGeometry(0, self.main_window_height - 3*lblInfoH, lblInfoW, lblInfoH)
        self.labelInfoSOG.setText("SOG")

        self.labelInfoSOGdata = QLabel(self)
        self.labelInfoSOGdata.setStyleSheet(styles.labelInfoTopRight)
        self.labelInfoSOGdata.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelInfoSOGdata.setGeometry(100, self.main_window_height - 3*lblInfoH, lblInfoW - 100, lblInfoH)

        self.labelInfoSCALE = QLabel(self)
        self.labelInfoSCALE.setStyleSheet(styles.labelInfo)
        self.labelInfoSCALE.setGeometry(0, self.main_window_height - 2*lblInfoH, lblInfoW, lblInfoH)
        self.labelInfoSCALE.setText("Scale")

        self.labelInfoSCALEdata = QLabel(self)
        self.labelInfoSCALEdata.setStyleSheet(styles.labelInfoRight)
        self.labelInfoSCALEdata.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelInfoSCALEdata.setGeometry(100, self.main_window_height - 2*lblInfoH, lblInfoW - 100, lblInfoH)

        self.logDataBool = False
        self.labelInfoDISTANCE = QLabel(self)
        self.labelInfoDISTANCE.setStyleSheet(styles.labelInfo)
        self.labelInfoDISTANCE.setGeometry(0, self.main_window_height - lblInfoH, lblInfoW, lblInfoH)
        self.labelInfoDISTANCE.setText("Logging")

        self.labelInfoDISTANCEdata = QLabel(self)
        self.labelInfoDISTANCEdata.setStyleSheet(styles.labelInfoRight)
        self.labelInfoDISTANCEdata.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelInfoDISTANCEdata.setGeometry(100, self.main_window_height - lblInfoH, lblInfoW - 100, lblInfoH)

        self.updateInfoLabels()
        self.currentDate = ''
        self.currentDepth = ''
        self.logList = []
        self.connection = self.initConnect()

        self.timer = QTimer()
        self.timerCount = 2000
        self.timer.timeout.connect(self.timeIsEnd)

        self.press_point = None

        path_coursor = os.path.join(self.path, 'icons', 'coursor1.png')
        coursor_pix = QPixmap(path_coursor)
        coursor = QCursor(coursor_pix)
        self.setCursor(coursor)
        self.coords_list = None
        self.selectPoints(self.connection)
        self.fishInfo = self.getFishIconsInfo()
        self.sendFishIcons(self.fishInfo)


    def selectPoints(self, conn):
        sqlite_select_query = "SELECT * from map_points"
        cursor = conn.cursor()
        cursor.execute(sqlite_select_query)
        self.coords_list = cursor.fetchall()
        cursor.close()

    def getFishIconsInfo(self):
        itog = []
        if self.coords_list is not None:
            for row in self.coords_list:
                ###   ('2023-07-06_00-44-35', 55.682383903131445, 37.878969192341394, 'button_3_1', 'home')  ###
                new_row = []
                point_coord = self.myWidget.getPointByCoords(row[1], row[2])
                _, y, x = row[3].split('_')
                icon = str(y + '_' + x)
                new_row = [point_coord[0], point_coord[1], icon, row[4], row[0]]
                itog.append(tuple(new_row))
        return itog

    def sendFishIcons(self, data):
        self.iconsWidget.getCoordsAndIcons(data)


    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path

    def screenShot(self):
        date = datetime.now()
        filename = date.strftime('%Y-%m-%d_%H-%M-%S.png')
        path_screenshot = os.path.join(self.path, 'screenshots', filename)
        p = self.grab()
        p.save(path_screenshot, 'png')

    def initSettings(self):
        filename = 'settings.ini'
        path_to_folder = os.path.join(self.path, 'settings')
        print("MW. Init Settings")
        if not os.path.exists(path_to_folder):
            os.makedirs(path_to_folder)
        path_settings = os.path.join(self.path, 'settings', filename)
        self.settings = QSettings(path_settings, QSettings.IniFormat)

    def startTimer(self):
        self.timer.start(self.timerCount)

    def setPointToAction(self, point=None):
        self.circles.setPointToAction(point)

    def timeIsEnd(self):
        print("send", self.mouse_old_pos)
        self.setPointToAction(self.mouse_old_pos)
        #TODO - еще проверять, виден ли кораблик!
        self.circles.setVisibleLine(True)
        self.timer.stop()
        dialog = PointMap(self)
        dialog.exec_()
        dialog.show()
        if dialog.icon_name != '':
            #print("USPEKH", dialog.icon_name, dialog.full_coords)
            date = datetime.now()
            filename = date.strftime('%Y-%m-%d_%H-%M-%S')
            data = {"name": "", "latitude": "", "longitude": "", "icon": ""}
            data["name"] = filename
            lat, lon = dialog.full_coords.split(',')
            data["latitude"] = float(lat)
            data["longitude"] = float(lon)
            data["icon"] = dialog.icon_name
            data["description"] = dialog.description
            print(data)
            self.insert2MP(self.connection, data)
            self.selectPoints(self.connection)
            data = self.getFishIconsInfo()
            print("dateika", data)
            self.sendFishIcons(data)

    def insert2MP(self, conn, data):
        cur = conn.cursor()
        try:
            print(data)
            cur.execute("INSERT INTO map_points VALUES (:name, :latitude, :longitude, :icon, :description)", data)
        except Exception as e:
            print(e)
        conn.commit()


    def insertDB(self, conn, table, data):
        cur = conn.cursor()
        try:
            print(data)
            cur.execute("INSERT INTO nmea_settings VALUES (:comport, :baudrate)", data)
        except Exception as e:
            print(e)
        conn.commit()

    def initConnect(self):
        if not os.path.exists('db'):
            os.makedirs('db')

        path = os.path.join(os.getcwd(), 'db', 'main_db.db')
        connection = sqlite3.connect(path)
        return connection

    def addImageDialog(self):
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
            self.addImage()

        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Chosen image file have not .kml file around!')

    def addImage(self):
        self.myWidget.addImage(fromParent = True)

    def writeLogs(self):

        if self.logDataBool:
            self.logDataBool = False
        else:
            self.logDataBool = True

    def loggingData(self, lat, lon, depth):
        if self.logDataBool:
            if self.currentDate != '':
                log_filename = str(self.currentDate) + '.csv'
                if os.path.exists(os.path.join(os.getcwd(), 'logs', log_filename)) == False:
                    fp = open(os.path.join(os.getcwd(), 'logs', log_filename), 'x')
                    fp.close()
                else:
                    if len(self.logList) <= 10:
                        cur_list = [str(lat), str(lon), str(depth)]
                        self.logList.append(cur_list)
                    else:
                        fw = open(os.path.join(os.getcwd(), 'logs', log_filename), 'a')
                        for data in self.logList:
                            #55.64206123352051,37.88592338562012,4.89
                            logStr = ','.join(data)
                            fw.write(logStr + '\n')
                        fw.close()
                        self.logList.clear()
                        cur_list = [str(lat), str(lon), str(depth)]
                        self.logList.append(cur_list)

    def updateInfoLabels(self):
        self.labelInfoSCALEdata.setText("{} m".format(str(int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]))))
        self.labelInfoSOGdata.setText("{} km/h".format(str(round(self.ship_speed, 1))))
        if self.logDataBool:
            self.labelInfoDISTANCEdata.setText("yes")
            self.labelInfoDISTANCEdata.setStyleSheet(styles.labelInfoRightYes)
        else:
            self.labelInfoDISTANCEdata.setText("no")
            self.labelInfoDISTANCEdata.setStyleSheet(styles.labelInfoRight)

    def getDepthMapFile(self):
        self.figure.clear()
        self.figure.clf()
        Settings.FILE_DEPTH_NAME = None
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Depth Data', r"", "CSV(*.csv);;All Files(*.*)")

        if file_name:
            # распарсим на ФАЙЛ и ПУТЬ
            filename = Path(file_name).name

            dir = Path(file_name).parent
            # распарсим ФАЙЛ на ИМЯ и РАСШИРЕНИЕ
            fileSourseName, fileSourseExtension = filename.split('.')
            Settings.FILE_DEPTH_NAME = file_name

            ########### ||||| вниз
            self.contour_data = pd.read_csv(Settings.FILE_DEPTH_NAME, header=None, names=['y', 'x', 'z'])
            print(type(self.contour_data))

            # Максимальные координаты карты глубин
            self.contour_max_x = self.contour_data['x'][np.argmax(self.contour_data['x'])]
            self.contour_min_x = self.contour_data['x'][np.argmin(self.contour_data['x'])]
            self.contour_max_y = self.contour_data['y'][np.argmax(self.contour_data['y'])]
            self.contour_max_z = self.contour_data['z'][np.argmax(self.contour_data['z'])]
            self.contour_min_y = self.contour_data['y'][np.argmin(self.contour_data['y'])]
            print(
                #self.contour_max_x,
                  #self.contour_min_x,
                  #self.contour_max_y,
                  #self.contour_min_y,
                  "max_depth:", self.contour_max_z)

    def plot(self):
        if Settings.FILE_DEPTH_NAME is not None:
            tic1 = time.perf_counter()
            self.figure.clear()
            #TODO - спорно... вообще тут разобраться...
            self.figure.clf()
            self.getCornersCoords()

            min_dolg = float(self.coordsNW.split(',')[1]) # 37.862728
            max_dolg = float(self.coordsNE.split(',')[1])
            min_shir = float(self.coordsSW.split(',')[0]) # 55.634530
            max_shir = float(self.coordsNW.split(',')[0])

            self.maxDepth = ceil(self.contour_data['z'].max())


            ind_min_x = np.where( (self.contour_data['x'] - min_dolg) <= 0,
                                 (self.contour_data['x'] - min_dolg) , -np.inf).argmax()
            ind_max_x = np.where( (self.contour_data['x'] - max_dolg) >= 0,
                                  (self.contour_data['x'] - max_dolg), np.inf).argmin()
            min_x = self.contour_data['x'][ind_min_x] if self.contour_min_x <= min_dolg else self.contour_min_x
            max_x = self.contour_data['x'][ind_max_x] if self.contour_max_x >= max_dolg else self.contour_max_x


            ind_min_y = np.where( (self.contour_data['y'] - min_shir) <= 0,
                                (self.contour_data['y'] - min_shir) , -np.inf).argmax()

            ind_max_y = np.where( (self.contour_data['y'] - max_shir) >= 0,
                                (self.contour_data['y'] - max_shir), np.inf).argmin()

            min_y = self.contour_data['y'][ind_min_y] if self.contour_min_y <= min_shir else self.contour_min_y
            max_y = self.contour_data['y'][ind_max_y] if self.contour_max_y >= max_shir else self.contour_max_y

            self.contour_data_fast = self.contour_data[(self.contour_data['x'] >= min_x) &
                                                       (self.contour_data['x'] <= max_x) &
                                                       (self.contour_data['y'] >= min_y) &
                                                       (self.contour_data['y'] <= max_y)]


            self.Z = self.contour_data_fast.pivot_table(index='x', columns='y', values='z').T.values
            #print(self.Z)
            self.X_unique = np.sort(self.contour_data_fast.x.unique())
            self.Y_unique = np.sort(self.contour_data_fast.y.unique())
            self.X, self.Y = np.meshgrid(self.X_unique, self.Y_unique)
            #func = si.bisplev(self.X, self.Y, self.Z)

            #z = np.take(func(38.047033039027504, 55.59210725456789), 0)
            #print("ZZZZZZZZZZ", func)

            '''
            self.Z = self.contour_data.pivot_table(index='x', columns='y', values='z').T.values
            self.X_unique = np.sort(self.contour_data.x.unique())
            self.Y_unique = np.sort(self.contour_data.y.unique())
            self.X, self.Y = np.meshgrid(self.X_unique, self.Y_unique)
            '''
            rcParams['toolbar'] = 'None'
            #print("self.Z", self.Z.size)
            if self.Z.size > 20:

                # rcParams['figure.figsize'] = 20, 10 # sets plot size
                self.ax = self.figure.add_subplot(111)

                self.cmap = ListedColormap(Settings.PLOT_PALETTE[self.settings.value('palette')])
                self.depth_arr = []

                for i in arange(0, self.maxDepth + 1, float(self.settings.value('freq_lines'))):
                    self.depth_arr.append(i)
                levels = np.array(self.depth_arr)

                # нарисовать и заполнить контуры

                self.cpf = self.ax.contourf(self.X, self.Y, self.Z,
                                            levels,
                                            cmap=self.cmap,
                                            alpha=float(self.settings.value('alpha_contour')),
                                            #antialiased=True,
                                            #nchunk=40,
                                            algorithm='mpl2014'
                                            )
                line_colors = ['black' for line in self.cpf.levels]

                # изолинии
                tic3 = time.perf_counter()
                self.cp = self.ax.contour(self.X, self.Y, self.Z,
                                          levels=levels,
                                          colors=line_colors,
                                          linewidths=0.4)
                tic4 = time.perf_counter()
                # количество градаций глубин для подписей
                clevels = []
                for i in arange(0, self.maxDepth + 1, float(self.settings.value('depth_lines'))):
                    clevels.append(i)

                # подписи линий
                tic5 = time.perf_counter()
                self.ax.clabel(self.cp,
                               fontsize=7,
                               colors='black', #line_colors,
                               levels=clevels,
                               # inline=False,
                               inline_spacing=2,
                               #manual=True
                               )
                tic6 = time.perf_counter()
                self.ax.set_position([0, 0, 1, 1])

                central_lat = (min_shir + max_shir) / 2
                mercator_aspect_ratio = 1 / cos(radians(central_lat)) #central_lat

                self.ax.set_aspect(mercator_aspect_ratio)
                plt.axis([min_dolg, max_dolg, min_shir, max_shir])
                plt.axis('off')
                self.canvas.draw()
            else:
                self.figure.clear()
                self.canvas.draw()
            ticEND = time.perf_counter()
            #print("ALL_TIME", ticEND - tic1, "self.cp: ", tic4 - tic3, "self.ax.clabel", tic6 - tic5, "canvas.draw()", ticEND - tic6)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = event.pos()
            self.myWidget.setLabelOldPos(self.myWidget.getCurrentLabelMapPos())
            self.myWidget.setLabelPillowOldPos(self.myWidget.getCurrentLabelPillowPos())
            #self.myWidget.setScreenOldPos(self.myWidget.getCurrentScreenCenter())
            self.shipWidget.setShipOldPos()
            self.iconsWidget.setIconsOldPos()
            self.ship_old_pos = self.myWidget.getCurrentLabelShipPos()

            current_pos = self.myWidget.getCurrentLabelMapPos()
            current_lat, current_lon = self.myWidget.getCoord(current_pos.x(), current_pos.y(),
                                           event.pos().x(), event.pos().y()).split(', ')
            self.currentPointToSave.setX(float(current_lat))
            self.currentPointToSave.setY(float(current_lon))
            self.startTimer()
        if event.button() == Qt.RightButton:
            pos = self.myWidget.getCurrentLabelMapPos()
            point = self.myWidget.getCoord(pos.x(), pos.y(),
                                           event.pos().x(), event.pos().y())  # event.pos().y() - self.titleBarHeight*2
            curLat1, curLon1 = point.split(', ')
            print("click! 1: 2: ", curLat1, curLon1, point)

    def mouseReleaseEvent(self, event):
        self.timer.stop()
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = None
            self.myWidget.doCentrPixels()
            if self.myWidget.getNewCenter() != '':
                Settings.CENTR_LAT, Settings.CENTR_LON = self.myWidget.getNewCenter().split(', ')
            #self.myWidget.pillowLabelSetImage()
            self.showStatusBarMessage()
            self.plot()

    def mouseMoveEvent(self, event):
        self.myWidget.makeMovingCenterFalse()
        self.myWidget.setPrevShipPodNone()

        self.gridWidget.move_grid_on()
        self.gridWidget.labelGridUpdate()
        self.gridWidget.proxyToGridPosition(self.myWidget.getLabelMapPosition())

        self.gridW.setCurrentMapPosition(self.myWidget.getLabelMapPosition())
        self.gridW.setModyfyed()
        self.gridW.update()
        #self.plot()

        if not self.mouse_old_pos:
            return
        delta = event.pos() - self.mouse_old_pos
        # TODO - конечно, это сильно спорно...
        #self.plot()
        self.myWidget.mooving(delta)
        self.shipWidget.mooving(delta)
        self.iconsWidget.moveIcons(delta)
        self.timer.stop()

    def mouseDoubleClickEvent(self, event):
        #print("MOUSE MW:", event.pos())
        pos = self.myWidget.getCurrentLabelMapPos()
        point = self.myWidget.getCoord(pos.x(), pos.y(),
                             event.pos().x(), event.pos().y()) #event.pos().y() - self.titleBarHeight*2
        curLat1, curLon1 = point.split(', ')
        print("click! 1: 2: ", curLat1, curLon1)

    def getCornersCoords(self):
        self.window_height = self.size().height()
        self.window_width = self.size().width()
        pos = self.myWidget.getCurrentLabelMapPos()

        self.coordsNW = self.myWidget.getCoord(pos.x(), pos.y(),
                             0, 0)
        self.coordsSW = self.myWidget.getCoord(pos.x(), pos.y(),
                             0, self.window_height)
        self.coordsNE = self.myWidget.getCoord(pos.x(), pos.y(),
                             self.window_width, 0)
        self.coordsSE = self.myWidget.getCoord(pos.x(), pos.y(),
                             self.window_width, self.window_height)

    def checkSettings(self, dialog = None, data = {}):

        if dialog is not None:
            if dialog == 'nmea' and data:
                self.insertDB(self.connection, 'nmea_settings', data)

        self.lineEditDebug.setText("")
        if (Settings.DEBUG_INFO == True):
            self.lineEditDebug.setVisible(True)
        else:
            self.lineEditDebug.setVisible(False)
        self.circles.checkVisible()
        self.circles.update()

    def zoomMinus(self):
        if self.current_scale < Settings.MASHTAB_MAX:
            self.current_scale = self.current_scale + 1
            Settings.CURRENT_MASHTAB = Settings.CURRENT_MASHTAB + 1
            self.updateScale()

    def zoomPlus(self):
        if self.current_scale > Settings.MASHTAB_MIN:
            self.current_scale = self.current_scale - 1
            Settings.CURRENT_MASHTAB = Settings.CURRENT_MASHTAB - 1
            self.updateScale()

    def updateScale(self):
        self.gridWidget.zoom_grid()
        self.gridW.zoom_grid()
        self.myWidget.updateScale(Settings.CURRENT_MASHTAB)
        self.showStatusBarMessage()
        self.plot()
        data = self.getFishIconsInfo()
        self.sendFishIcons(data)
        self.updateInfoLabels()
        #self.statusBar.showMessage(strStatus)

    def showStatusBarMessage(self):
        pass

    def createGrid(self):
        self.gridW.createGrid()

    '''
    def setCenterMoving(self):
        if self.keepCenter == False:
            self.keepCenter = True
            self.myWidget.setMovingCenter()
            self.buttonKeep.setIcon(QIcon('icons/target_ok.png'))
        else:
            self.buttonKeep.setIcon(QIcon('icons/target.png'))
            self.keepCenter = False
            self.myWidget.setMovingCenter()
    '''

    def openMNEAsettingsWindow(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
        dialog.show()

    def openMAPsettingsWindow(self):
        dialog = SettingsMap(self)
        dialog.exec_()
        dialog.show()

    def waitingSerial(self):
        print("1. waitingSerial")
        self.lineEditDebug.setText("")
        try:
            if Settings.COM_PORT_EKHO is not None and (self.serial.isOpen() == False):
                self.serial.setPortName(Settings.COM_PORT_EKHO)
                self.serial.setBaudRate(int(Settings.BAUD_RATE))
                conn = self.serial.open(QIODevice.ReadOnly)
                print("2. waitingSerial conn ", conn)
                if conn == True:
                    print("3.1 waitingSerial conn True")
                    rdy = self.serial.readyRead.connect(self.onRead)
                    print("3.2 waitingSerial conn True", rdy)
                else:
                    print("3.3 waitingSerial conn not true")

            elif self.serial.isOpen() == True:
                self.serial.close()
                print("serial -> close!")
                self.shipWidget.clearLabelShip()

        except Exception as e:
            print(e, ' waitingSerial')

    def onRead(self):
        buffer = ''
        rxs = ''
        try:
            buffer = self.serial.readLine()
            rxs = str(buffer, 'utf-8')
        except Exception as e:
            print(e, ' onRead')

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
                        if self.lineEditDebug.isVisible() == True:
                            self.lineEditDebug.append(self.strData)
                    self.strData = ''
        except Exception as e:
            print(e, ' buffer ', self.strData)

    def parsingDepthData(self, str):
        data = str.split(',')
        if (len(data) == 7):
            strDepth = data[3]
            self.currentDepth = round(float(strDepth), 1)
            try:
                self.labelDepth.setText("{}".format(self.currentDepth))
            except Exception as e:
                print(e, ' parsingDepthData')
        else:
            print("Invalide qnt of data - 7")

    def parsingGPSData(self, str):
        try:
            data = str.split(',')
            if (len(data) == 13):
                if data[2] == 'A':
                    currentTime = data[1]
                    tim = currentTime.split('.')
                    time = tim[0]
                    timeNorm = datetime.strptime(time, '%H%M%S') + timedelta(hours=3)
                    #self.LCDtime.display(timeNorm.strftime('%H:%M'))
                    self.currentDate = data[9]
                    course = int(data[8])
                    Lat = data[3]
                    LatSign = data[4]
                    Lon = data[5]
                    LonSign = data[6]
                    strSpeed = data[7]
                    self.ship_speed = float(data[7]) * 1.85
                    LatDEC = self.NMEA2decimal(Lat, LatSign)
                    LonDEC = self.NMEA2decimal(Lon, LonSign)
                    #print(LatDEC, LonDEC)
                    if course in range(0, 360):
                        pass
                        #self.LCDcourse.display(int(course))
                    #self.LCDspeed.display(speed)
                    ship_coords = self.myWidget.getPointByCoordsCorner(LatDEC, LonDEC)
                    new_x, new_y = ship_coords
                    self.shipWidget.moveLabelShip(new_x, new_y, int(course))
                    self.circles.setShipPosition(new_x, new_y, int(course))
                    self.updateInfoLabels()

                    self.loggingData(LatDEC, LonDEC, self.currentDepth)
                    #self.shipWidget.newGPScoordinates(LatDEC, LonDEC, int(course))
                else:
                    now = QTime.currentTime()
                    print(now.toString(), " GPS coordinates are not valid yet. GPS sends", data[2], "value... Waiting...")
            else:
                print("Invalide qnt of data - 13")
        except Exception as e:
            print(e, " parsing parsingGPSData")

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

class MyQLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, widget):
        super().__init__(widget)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()


class PointMap(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowTitle("Point options...")
        self.mainWindow = MainWindow
        self.path = self.getPath()
        path_images = os.path.join(self.path, 'icons', 'fishIcons.png')
        self.pixmap_icons = QPixmap(path_images)
        windowW = 330
        windowH = 150
        self.setGeometry(0, 0, windowW, windowH)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setWindowOpacity(0.2)
        self.setStyleSheet("background-color:rgba(53,57,63);")


        self.labelPoint = QLabel(self)
        self.labelPoint.setText("Point:")
        self.labelPoint.setStyleSheet(styles.map_button)
        self.labelPoint.setGeometry(1, 20, int(windowW / 5) - 1, 39)

        self.labelPointLatLon = QLabel(self)
        self.labelPointLatLon.setStyleSheet(styles.map_button)
        coords_str = str(round(self.mainWindow.currentPointToSave.x(), 6)) + ", " + str(round(self.mainWindow.currentPointToSave.y(), 6))
        self.full_coords = str(self.mainWindow.currentPointToSave.x()) + "," + str(self.mainWindow.currentPointToSave.y())
        self.labelPointLatLon.setText(coords_str)
        self.labelPointLatLon.setGeometry(70, 20, 190, 39)

        self.buttonIMAGE = QPushButton(self)
        self.buttonIMAGE.setStyleSheet(styles.map_button)
        self.buttonIMAGE.setText("IMG")
        self.buttonIMAGE.setGeometry(265, 20, 60, 39)
        self.buttonIMAGE.clicked.connect(self.choseImage)

        self.labelText = QLabel(self)
        self.labelText.setText("Descr:")
        self.labelText.setStyleSheet(styles.map_button)
        self.labelText.setGeometry(1, 67, int(windowW / 5) - 1, 39)

        self.editText = MyQLineEdit(self)
        self.editText.setText("")
        self.editText.setStyleSheet(styles.map_button)
        self.editText.setGeometry(71, 67, int(windowW) - 72, 39)
        self.editText.clicked.connect(self.inputText)

        self.buttonSAVE = QPushButton(self)
        self.buttonSAVE.setText("Save")
        self.buttonSAVE.setStyleSheet(styles.map_button)
        self.buttonSAVE.setGeometry(1, int(windowH - 40), int(windowW/3) - 1, 39)
        self.buttonSAVE.clicked.connect(self.returnOK)

        self.buttonDIST = QPushButton(self)
        self.buttonDIST.setText("Distance")
        self.buttonDIST.setStyleSheet(styles.map_button)
        self.buttonDIST.setGeometry(int(windowW/3 + 1), int(windowH - 40), int(windowW/3) - 1, 39)

        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setText("Cancel")
        self.buttonNOT.setStyleSheet(styles.map_button)
        self.buttonNOT.setGeometry(int(2*windowW/3 + 1), int(windowH - 40), int(windowW/3) - 1, 39)
        self.buttonNOT.clicked.connect(self.returnNOT)
        self.icon_name = ''
        self.description = ''
        self.setCenter()

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path

    def returnOK(self):
        self.mainWindow.setPointToAction()
        self.close()

    def returnNOT(self):
        self.mainWindow.setPointToAction()
        self.icon_name = ''
        self.close()

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def choseImage(self):
        dialog = FishIcons(self)
        dialog.exec_()
        dialog.show()
        self.icon_name = str(dialog.button_check)
        if self.icon_name != "":
            _, y, x = self.icon_name.split('_')
            req = QRect(QPoint(int(x) * 22, int(y) * 22), QPoint(int(x) * 22 + 21, int(y) * 22 + 21))
            pix = self.pixmap_icons.copy(req)
            icon = QIcon(pix)
            self.buttonIMAGE.setText('')
            self.buttonIMAGE.setIcon(icon)
            self.buttonIMAGE.setIconSize(QSize(22, 22))

    def inputText(self):
        dialog_keyboard = Keyboard(self)
        dialog_keyboard.exec_()
        dialog_keyboard.show()
        self.description = str(dialog_keyboard.result_text)
        if self.description != "":
            self.editText.setText(self.description)


class Keyboard(QDialog):
    def __init__(self, PointMap):
        super().__init__(parent=PointMap)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.mainWindow = PointMap
        windowW = 900
        windowH = 250
        button_size = QSize(22, 22)
        self.setGeometry(0, 0, windowW, windowH)
        self.setStyleSheet("background-color:rgba(53,57,63);")

        vert_lay = QVBoxLayout()
        self.editText = MyQLineEdit(self)
        self.editText.setText("")
        self.editText.setStyleSheet(styles.map_button)
        self.editText.setGeometry(3, 1, int(windowW), 29)
        vert_lay.addWidget(self.editText)


        self.grid = QGridLayout()
        self.setButtons()
        vert_lay.addLayout(self.grid)


        hor_lay = QHBoxLayout()
        self.buttonOK = QPushButton(self)
        self.buttonOK.setText("OK")
        self.buttonOK.setStyleSheet(styles.map_button)
        self.buttonOK.clicked.connect(self.returnOK)

        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setText("NO")
        self.buttonNOT.setStyleSheet(styles.map_button)
        self.buttonNOT.clicked.connect(self.returnNOT)
        hor_lay.addWidget(self.buttonOK, alignment=QtCore.Qt.AlignBottom)
        hor_lay.addWidget(self.buttonNOT, alignment=QtCore.Qt.AlignBottom)

        vert_lay.addLayout(hor_lay)

        self.setLayout(vert_lay)
        self.setCenter()
        self.result_text = ""

        self.upper_text = False

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)) + 100)

    def setButtons(self):
        names = ['1','2','3','4','5','6','7','8','9','0',
'q','w','e','r','t','y','u','i','o','p',
'UP','a','s','d','f','g','h','j','k','l',
'.','z','x','c','v','b','n','m','-','=',
'','','','PRB','','','','Backsp']

        positions = [(i, j) for i in range(5) for j in range(10)]
        for position, name in zip(positions, names):
            if name == '':
                continue
            button = QPushButton(name)
            button.setStyleSheet(styles.keyboard)
            button.setObjectName(name)
            if name == 'UP':
                button.setCheckable(True)
            button.clicked.connect(self.clickButton)
            if name == 'PRB':
                button.setFixedWidth(250)
                self.grid.addWidget(button, *position, 1, 4, alignment=QtCore.Qt.AlignCenter)
            else:
                self.grid.addWidget(button, *position, alignment=QtCore.Qt.AlignCenter)

    def clickButton(self):
        butt = self.sender()
        self.button_check = str(butt.objectName())
        if self.button_check not in ('Backsp','UP','PRB'):
            if self.upper_text:
                self.button_check = self.button_check.upper()
            self.editText.setText(self.editText.text() + self.button_check)
        elif self.button_check == 'PRB':
            self.editText.setText(self.editText.text() + " ")
        elif self.button_check == 'Backsp':
            self.editText.setText(self.editText.text()[:-1])
        elif self.button_check == 'UP':
            if self.upper_text:
                self.upper_text = False
            else:
                self.upper_text = True
        self.result_text = self.editText.text()

    def returnOK(self):
        self.close()

    def returnNOT(self):
        self.result_text = ''
        self.close()


class FishIcons(QDialog):
    def __init__(self, PointMap):
        super().__init__(parent=PointMap)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.mainWindow = PointMap
        windowW = 250
        windowH = 180
        self.setGeometry(0, 0, windowW, windowH)
        self.setStyleSheet("background-color:rgba(53,57,63);")
        #TODO - ниже нужно перенести в Point, так будет удобнее!

        self.pixmap = self.mainWindow.pixmap_icons
        icon_param = 22
        icons_width = self.pixmap.width()
        icons_height = self.pixmap.height()
        self.grid = QGridLayout()

        self.setButtons(icons_width, icons_height, icon_param)
        self.setLayout(self.grid)
        '''
        self.buttonSAVE = QPushButton(self)
        self.buttonSAVE.setText("Ok")
        self.buttonSAVE.setStyleSheet(styles.map_button)
        self.buttonSAVE.setGeometry(1, int(windowH - 30), int(windowW/2) - 1, 29)
        self.buttonSAVE.clicked.connect(self.returnOK)

        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setText("Cancel")
        self.buttonNOT.setStyleSheet(styles.map_button)
        self.buttonNOT.setGeometry(int(windowW/2 + 1), int(windowH - 30), int(windowW/2) - 1, 29)
        self.buttonNOT.clicked.connect(self.returnNOT)
        '''
        self.setCenter()
        self.button_check = ""

    def setButtons(self, icons_width, icons_height, icon_param):
        rangeX = int(icons_width/icon_param)
        rangeY = int(icons_height / icon_param)
        for j in range(rangeY):
            for i in range(rangeX):
                req = QRect(QPoint(i*icon_param, j*icon_param), QPoint(i*icon_param + 21, j*icon_param + 21))
                pix = self.pixmap.copy(req)
                icon = QIcon(pix)

                button = QPushButton(self)
                #button.setCheckable(True)
                button.setIcon(icon)
                button.setIconSize(QSize(icon_param, icon_param))
                button.setStyleSheet(styles.iconFish)
                name = 'button_' + str(j) + '_' + str(i)
                button.setObjectName(name)
                button.clicked.connect(self.clickButton)
                '''
                button = QLabel(self)
                button.setPixmap(pix)
                '''
                self.grid.addWidget(button, j, i, alignment=QtCore.Qt.AlignTop)

    def clickButton(self):
        butt = self.sender()
        self.button_check = str(butt.objectName())
        self.close()

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)) + 60)

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path

    '''
    def returnNOT(self):
        self.button_check = ""
        self.close()

    def returnOK(self):
        self.close()
    '''

class SettingsMap(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)
        self.path = self.getPath()
        self.initSettings()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet(styles.map_dialog)
        self.mainWindow = MainWindow
        self.setWindowTitle("Map Settings")
        windowW = 700
        windowH = 300
        self.setGeometry(0, 0, windowW, windowH)
        self.setCenter()

        self.base_y = 20

        self.labelNeedCircles = QLabel(self)
        self.labelNeedCircles.setStyleSheet(styles.group_box_label)
        self.labelNeedCircles.setText('Circles:')

        self.checkCircles = QCheckBox(self)
        #self.checkCircles.move(70, self.base_y)
        if Settings.NEED_FISHING_CIRCLE:
            self.checkCircles.setCheckState(True)
        else:
            self.checkCircles.setCheckState(False)

        self.labelNeedVector = QLabel(self)
        self.labelNeedVector.setStyleSheet(styles.group_box_label)
        self.labelNeedVector.setText('Vector:')
        #self.labelNeedVector.move(5, self.base_y + 30)

        self.checkVector = QCheckBox(self)
        #self.checkVector.move(70, self.base_y + 30)
        if Settings.NEED_RADIUS_VECTOR:
            self.checkVector.setCheckState(True)
        else:
            self.checkVector.setCheckState(False)

        self.labelQntCircles = QLabel(self)
        self.labelQntCircles.setText('Qnt circles:')
        self.labelQntCircles.setStyleSheet(styles.group_box_label)

        self.labelQntCirclesCOUNT = QLabel(self)
        self.labelQntCirclesCOUNT.setStyleSheet(styles.group_box_label)
        self.labelQntCirclesCOUNT.setText(str(Settings.FISHING_SIRCLE_QNT))

        self.qntCircles = QSlider(self)
        self.qntCircles.invertedControls()
        self.qntCircles.setMinimum(1)
        self.qntCircles.setMaximum(4)
        self.qntCircles.setPageStep(1)
        #self.qntCircles.setSliderPosition(Settings.FISHING_SIRCLE_QNT)
        self.qntCircles.setTickInterval(1)
        self.qntCircles.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.qntCircles.valueChanged.connect(self.updateQntCircles)

        self.labelRadCircles = QLabel(self)
        self.labelRadCircles.setStyleSheet(styles.group_box_label)
        self.labelRadCircles.setText('Rad circle:')


        self.labelRadCirclesMetr = QLabel(self)
        self.labelRadCirclesMetr.setStyleSheet(styles.group_box_label)
        self.labelRadCirclesMetr.setText(str(Settings.FISHING_SIRCLE_RADIUS))

        self.CirclesRad = QSlider(self)
        self.CirclesRad.invertedControls()
        self.CirclesRad.setMinimum(20)
        self.CirclesRad.setMaximum(90)
        self.CirclesRad.setPageStep(10)
        self.CirclesRad.setSliderPosition(Settings.FISHING_SIRCLE_RADIUS)
        self.CirclesRad.setTickInterval(10)
        self.CirclesRad.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.CirclesRad.valueChanged.connect(self.updateRadCircles)

        ###
        self.labelColorCircles = QLabel(self)
        self.labelColorCircles.setStyleSheet(styles.group_box_label)
        self.labelColorCircles.setText('Color:')

        self.buttonColor = QPushButton(self)
        self.buttonColor.setStyleSheet(styles.map_button)
        if Settings.CIRCLE_COLOR is not None:
            self.buttonColor.setStyleSheet(
                "background-color:{};".format(Settings.CIRCLE_COLOR)
            )
        self.buttonColor.setFixedSize(30, 30)
        self.buttonColor.clicked.connect(self.colorDialog)

        self.labelPalette = QLabel(self)
        self.labelPalette.setStyleSheet(styles.group_box_label)
        self.labelPalette.setText('Palette:')

        self.comboPalettes = QComboBox(self)
        self.comboPalettes.setStyleSheet(styles.combo_box)
        self.comboPalettes.addItems(list(Settings.PLOT_PALETTE.keys()))

        self.labelAlphaContour = QLabel(self)
        self.labelAlphaContour.setStyleSheet(styles.group_box_label)
        self.labelAlphaContour.setText('Alpha:')

        self.comboAlphaContour = QComboBox(self)
        self.comboAlphaContour.setStyleSheet(styles.combo_box)
        self.comboAlphaContour.addItems(Settings.ALPHA_CONTOURS)

        self.labelFreqLines = QLabel(self)
        self.labelFreqLines.setStyleSheet(styles.group_box_label)
        self.labelFreqLines.setText('Freq line:')

        self.comboFreqLines = QComboBox(self)
        self.comboFreqLines.setStyleSheet(styles.combo_box)
        self.comboFreqLines.addItems(Settings.FREQUENCIES_LINES)

        self.labelDepthLines = QLabel(self)
        self.labelDepthLines.setStyleSheet(styles.group_box_label)
        self.labelDepthLines.setText('Depth line:')

        self.comboDepthLines = QComboBox(self)
        self.comboDepthLines.setStyleSheet(styles.combo_box)
        self.comboDepthLines.addItems(Settings.DEPTH_LINES)
        ####


        self.groupBoxCircles = QGroupBox(self)
        vbox = QHBoxLayout(self)
        vbox.addWidget(self.labelNeedCircles)
        vbox.addWidget(self.checkCircles)
        vbox.addWidget(self.labelQntCircles)
        vbox.addWidget(self.labelQntCirclesCOUNT)
        vbox.addWidget(self.qntCircles)
        vbox.addWidget(self.labelRadCircles)
        vbox.addWidget(self.labelRadCirclesMetr)
        vbox.addWidget(self.CirclesRad)
        self.groupBoxCircles.setLayout(vbox)
        self.groupBoxCircles.setGeometry(5, 15, windowW - 10, 50)
        self.groupBoxCircles.setStyleSheet(styles.group_box)

        self.groupBoxVector = QGroupBox(self)
        vbox_vector = QHBoxLayout(self)
        vbox_vector.addWidget(self.labelNeedVector)
        vbox_vector.addWidget(self.checkVector)
        self.groupBoxVector.setLayout(vbox_vector)
        self.groupBoxVector.setGeometry(5, 70, 120, 50)
        self.groupBoxVector.setStyleSheet(styles.group_box)

        self.groupBoxContours = QGroupBox(self)
        gridBox = QHBoxLayout(self)
        gridBox.addWidget(self.labelColorCircles)
        gridBox.addWidget(self.buttonColor)
        gridBox.addWidget(self.labelPalette)
        gridBox.addWidget(self.comboPalettes)
        gridBox.addWidget(self.labelAlphaContour)
        gridBox.addWidget(self.comboAlphaContour)
        gridBox.addWidget(self.labelFreqLines)
        gridBox.addWidget(self.comboFreqLines)
        gridBox.addWidget(self.labelDepthLines)
        gridBox.addWidget(self.comboDepthLines)
        self.groupBoxContours.setLayout(gridBox)
        self.groupBoxContours.setGeometry(5, 125, windowW - 10, 50)
        self.groupBoxContours.setStyleSheet(styles.group_box)

        self.load_settings()

        self.buttonOK = QPushButton(self)
        self.buttonOK.setGeometry(1, int(windowH - 40), int(windowW / 2), 39)
        self.buttonOK.setStyleSheet(styles.map_button)
        self.buttonOK.setText("Save")
        self.buttonOK.clicked.connect(self.returnOK)

        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setText("Cancel")
        self.buttonNOT.setStyleSheet(styles.map_button)
        self.buttonNOT.setGeometry(int(windowW/2 + 1), int(windowH - 40), int(windowW/2), 39)
        self.buttonNOT.clicked.connect(self.returnNOT)

    def getPath(self):
        path = os.getcwd()
        is_home = False
        for dir in os.listdir(path='.'):
            if dir == 'icons':
                is_home = True
        if not is_home:
            path = os.path.join(os.getcwd(), 'pyplotter')
        return path

    def initSettings(self):
        filename = 'settings.ini'
        path_to_folder = os.path.join(self.path, 'settings')
        print("SettingsMap. Init Settings")
        if not os.path.exists(path_to_folder):
            os.makedirs(path_to_folder)
        path_settings = os.path.join(self.path, 'settings', filename)
        self.settings = QSettings(path_settings, QSettings.IniFormat)

    def load_settings(self):
        ### QNT CIRCLES
        qnt_cirlces = self.settings.value('qnt_cirlces')
        print("qnt_cirlces", qnt_cirlces)
        if qnt_cirlces is not None:
            self.qntCircles.setSliderPosition(int(qnt_cirlces))
        else:
            self.qntCircles.setSliderPosition(Settings.FISHING_SIRCLE_QNT)

        ### COLOR CIRCLES
        color_circles = self.settings.value('color_circles')
        if color_circles is not None:
            self.buttonColor.setStyleSheet('background-color: {};'.format(color_circles))
            Settings.CIRCLE_COLOR = color_circles
        else:
            color_circles = '#28fd28'
        self.color_circles = QColor(color_circles)

        ### PALETTE
        palette = self.settings.value('palette')
        if palette is not None:
            self.comboPalettes.setCurrentText(palette)
            Settings.CURRENT_PALETTE = palette

        ### freq_lines
        freq_lines = self.settings.value('freq_lines')
        if freq_lines is not None:
            self.comboFreqLines.setCurrentText(str(freq_lines))

        alpha_contour = self.settings.value('alpha_contour')
        if alpha_contour is not None:
            self.comboAlphaContour.setCurrentText(str(alpha_contour))

        ### freq isolines depth
        depth_lines = self.settings.value('depth_lines')
        if depth_lines is not None:
            self.comboDepthLines.setCurrentText(str(depth_lines))




    def save_settings(self):
        vector = self.checkVector.isChecked()
        circles = self.checkCircles.isChecked()
        qnt_cirlces = self.qntCircles.value()
        rad_circles = self.CirclesRad.value()
        color_circles = self.color_circles.name()

        palette = self.comboPalettes.currentText()
        alpha_contour = float(self.comboAlphaContour.currentText())
        freq_lines = float(self.comboFreqLines.currentText())
        depth_lines = float(self.comboDepthLines.currentText())

        self.settings.setValue('vector', vector)
        self.settings.setValue('circles', circles)
        self.settings.setValue('qnt_cirlces', qnt_cirlces)
        self.settings.setValue('rad_circles', rad_circles)
        self.settings.setValue('color_circles', color_circles)
        self.settings.setValue('palette', palette)
        self.settings.setValue('alpha_contour', alpha_contour)
        self.settings.setValue('freq_lines', freq_lines)
        self.settings.setValue('depth_lines', depth_lines)

    def colorDialog(self):
        qi = QColorDialog()
        self.color_circles = qi.getColor(QColor(40, 253, 40), None)
        self.buttonColor.setStyleSheet('background-color: {};'.format(self.color_circles.name()))
        print(self.color_circles.name())
        Settings.CIRCLE_COLOR = self.color_circles.name()

    def updateRadCircles(self):
        self.labelRadCirclesMetr.setText(str(self.CirclesRad.value()))
        Settings.FISHING_SIRCLE_RADIUS = self.CirclesRad.value()

    def updateQntCircles(self):
        self.labelQntCirclesCOUNT.setText(str(self.qntCircles.value()))
        Settings.FISHING_SIRCLE_QNT = self.qntCircles.value()

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def returnOK(self):
        self.save_settings()
        if (self.checkCircles.isChecked() == True):
            Settings.NEED_FISHING_CIRCLE = True
        else:
            Settings.NEED_FISHING_CIRCLE = False

        if (self.checkVector.isChecked() == True):
            Settings.NEED_RADIUS_VECTOR = True
        else:
            Settings.NEED_RADIUS_VECTOR = False

        Settings.CURRENT_PALETTE = self.comboPalettes.currentText()
        Settings.ALPHA_CONTOUR = float(self.comboAlphaContour.currentText())
        Settings.CURRENT_FREQUENCY_LINES = float(self.comboFreqLines.currentText())
        self.mainWindow.checkSettings()
        self.accept()

    def returnNOT(self):
        self.close()


class SettingsDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet(styles.nmeadialog)
        self.mainWindow = MainWindow
        self.setWindowTitle("NMEA Settings")
        windowX = 400
        windowY = 200
        self.setGeometry(0, 0, windowX, windowY)

        self.labelPort = QLabel(self)
        self.labelPort.setStyleSheet(styles.labels)
        self.labelPort.setText('COM port:')
        self.labelPort.move(55, 20)

        self.comboPorts = QComboBox(self)
        self.comboPorts.setGeometry(155, 14, 120, 30)
        self.comboPorts.setStyleSheet(styles.combobox)
        self.comboPorts.currentIndexChanged.connect(self.setPortName)


        self.labelPortName = QLabel(self)
        self.labelPortName.setText('COM port name')
        self.labelPortName.move(35, 47)

        self.labelBaudRate = QLabel(self)
        self.labelBaudRate.setText('Baud rate:')
        self.labelBaudRate.setStyleSheet(styles.labels)
        self.labelBaudRate.move(55, 73)

        self.comboBaud = QComboBox(self)
        self.comboBaud.addItems(Settings.BAUD_RATES)
        self.comboBaud.setStyleSheet(styles.combobox)
        self.comboBaud.setGeometry(155, 67, 120, 30)

        self.labelDebugData = QLabel(self)
        self.labelDebugData.setText('Debug GPS:')
        self.labelDebugData.setStyleSheet(styles.labels)
        self.labelDebugData.move(55, 120)

        self.checkDebug = QCheckBox(self)
        self.checkDebug.move(155, 122)
        self.checkDebug.setCheckState(False)

        self.portList = []
        self.portListFull = {}
        self.ComPorts = self.setPorts()

        self.buttonOK = QPushButton(self)
        self.buttonOK.setStyleSheet(styles.buttons)

        self.buttonOK.setText("Save")
        self.buttonOK.setGeometry(1, int(windowY - 40), int(windowX/2), 39)
        self.buttonOK.clicked.connect(self.returnOK)

        self.buttonNOT = QPushButton(self)
        self.buttonNOT.setStyleSheet(styles.buttons)
        self.buttonNOT.setText("Cancel")
        self.buttonNOT.setGeometry(int(windowX/2 + 1), int(windowY - 40), int(windowX/2), 39)
        self.buttonNOT.clicked.connect(self.returnNOT)

        self.setCenter()

    def setPortName(self):
        port_name = self.comboPorts.currentText()
        self.labelPortName.setText(self.portListFull.get(port_name))

    def setCenter(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def setPorts(self):

        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            name = port.portName()
            descr = port.description()
            self.portList.append(name)
            self.portListFull[name] = descr
        self.comboPorts.addItems(self.portList)

    def returnOK(self):
        list = {"comport": "", "baudrate": ""}
        list["comport"] = self.comboPorts.currentText()
        list["baudrate"] = self.comboBaud.currentText()
        Settings.BAUD_RATE = self.comboBaud.currentText()
        Settings.COM_PORT_EKHO = self.comboPorts.currentText()
        if(self.checkDebug.isChecked() == True):
            Settings.DEBUG_INFO = True
        else:
            Settings.DEBUG_INFO = False
        print(list)
        self.mainWindow.checkSettings('nmea', list)
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