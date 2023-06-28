#!/usr/bin/python3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QFileDialog, QLabel, QWidget, QMainWindow, QApplication, QSlider, \
    QAction, qApp, QToolBar, QStackedWidget, QPushButton, QDesktopWidget, QComboBox, QLCDNumber, QLineEdit, QCheckBox, \
    QTextEdit, QTextBrowser, QStackedLayout, QColorDialog, QMenu, QToolButton, QVBoxLayout
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
from PyQt5.QtCore import Qt, QPoint, QRect, QIODevice, QSize, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon, QFont, QImage
from PyQt5.Qt import QTransform, QStyle, QStyleOptionTitleBar
from datetime import *
from PyQt5.QtCore import QTime
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
#############
import stylescss as styles
from PIL import Image, ImageOps, ImageFilter
from PIL.ImageQt import ImageQt
import sqlite3

label_map_pos = QPoint(423, -1975)
labelmap_size = QSize(1309, 8465)

label_map_rect = QRect(label_map_pos, labelmap_size)

screen_pos = QPoint(0, -200)
screen_size = QSize(1920, 1080)
rect_screen = QRect(screen_pos, screen_size)

cross_reqt = rect_screen.intersected(label_map_rect)

print(cross_reqt)