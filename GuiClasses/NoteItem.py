from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
import pyqtgraph as pg
from pathlib import Path
from PyQt5.QtCore import (QPointF, QRectF, QLineF, QRect, Qt, QObject, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout )
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtSvg import QGraphicsSvgItem
from pyqtgraph.Qt import QtGui
import numpy as np
import pyqtgraph as pg

class NoteItem(QGraphicsSvgItem):
    def __init__(self, parent, staffInd, lineInd, horInd, startTick, duration):
        super().__init__(parent)
        self.staffInd = staffInd
        self.lineInd = lineInd
        self.horInd = horInd
        self.startTick = startTick
        self.duration = duration
