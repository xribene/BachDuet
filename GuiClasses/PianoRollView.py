from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import numpy as np
from pathlib import Path
from PyQt5.QtCore import (QPointF, QRectF, QLineF, QRect, Qt, QObject, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QGraphicsPixmapItem )
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtSvg import QGraphicsSvgItem
from GuiClasses.StaffItem import *
import pyqtgraph as pg
#from GraphicsItems.NoteItem import *

class PianoRollView(pg.PlotWidget):
    def __init__(self,appctxt, parent):
        super().__init__()
        self.parent = parent
        self.setMouseEnabled(x=True, y=True)
        self.appctxt = appctxt
        
        self.plotCurve1 = pg.PlotCurveItem()
        self.plotCurve2 = pg.PlotCurveItem()
        
        self.getPlotItem().addItem(self.plotCurve1)
        self.getPlotItem().addItem(self.plotCurve2)
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

        image = QtGui.QPixmap(self.appctxt.get_resource('Images/keysBackGrey.png'))
        keysImg = QGraphicsPixmapItem(image)
        keysImg.setZValue(-100)

        self.invertX(True)
        self.addItem(keysImg)  

    
   