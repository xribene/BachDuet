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
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout )
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtSvg import QGraphicsSvgItem
from GuiClasses.StaffItem import *
#from GraphicsItems.NoteItem import *

class StaffView(QGraphicsView):
    startStaffPainterSignal = pyqtSignal()
    updatePaintersRectSignal = pyqtSignal(float)
    def __init__(self,appctxt, parent):
        QGraphicsView.__init__(self, parent)
        self.parent = parent
        self.setMouseTracking(True)
        self.staffScene = QGraphicsScene(self)
        self.setScene(self.staffScene)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # image = QtGui.QImage("paperTexture.jpg")
        backGroundPath = Path(appctxt.get_resource('Images/paperTextureWhiteRes.jpg'))
        backGroundPath = backGroundPath.as_posix()
        self.setStyleSheet(f"background-image:url({backGroundPath}); background-attachment:fixed")
        # print(backGroundPath)
        #self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.viewport().setCursor(QtCore.Qt.CrossCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.se
        #print(self.geometry())
        #print(self.mapToScene(self.viewport().geometry()).boundingRect())
        #self.setSceneRect(0,0,1000,500)
        #self.translate(100,100)
        # FLAGS
        self.ctrlPressed = False
        self.minZoomFactor = 0.1
        self.maxZoomFactor = 10
        self.currentZoomFactor = 1
        self.current_timer = QTimer()
        self.current_timer.timeout.connect(self.addStaffs)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(500)

    @pyqtSlot(list, int)
    def updateStaffView(self, items, mode):
        for item in items:
            if mode == 1:
                self.staffScene.addItem(item)
            elif mode == 0:
                self.staffScene.removeItem(item)


    def addStaffs(self):
        #print("SRGPSRJGPSRIGPSRIJGPRSIJG")
        sceneBoudingRect = self.mapToScene(self.viewport().geometry()).boundingRect()
        
        self.staffLines = Staff(boundingRect = sceneBoudingRect)
        self.staffScene.addItem(self.staffLines)
        self.startStaffPainterSignal.emit()           
    
    @pyqtSlot(str)
    def ctrlKeyReceiver(self, action):
        if action == 'press':
            print("PATISA CONTROLL")
            self.ctrlPressed = True
            #print(self.svgItem.boundingRect())
        elif action == 'release':
            print("AFISA CONTROL")
            self.ctrlPressed = False
    def mouseMoveEvent(self, event):
        #print('mouseMoveEvent: pos {}'.format(event.pos()))
        #print(self.mapToScene(event.pos()))
        pass
    def wheelEvent2(self,event):
        print(event.angleDelta() )
        print(event.pixelDelta())
        delta = event.angleDelta().y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta/10)
    def showEvent(self, event):
        #super(CustomWidget, self).showEvent(event)
        print(f"showEvent selfMax {self.isMaximized()}, parentMax {self.parent.isMaximized()}")
    def wheelEvent(self, event):
        #print("WHEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEL")
        #print(event.angleDelta())
        #print(event.pixelDelta().isNull())
        if self.ctrlPressed: 
            if event.angleDelta().y() > 0:
                #print("GIATIDENZOUMAREISSSSSSSSSSSSS")
                self.currentZoomFactor += 0.1
            else:
                self.currentZoomFactor -= 0.1
            self.currentZoomFactor = max(self.minZoomFactor, min(self.currentZoomFactor, self.maxZoomFactor))
            #self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)#self.AnchorUnderMouse)
            #print(self.currentZoomFactor)
            self.setTransform(QTransform(self.currentZoomFactor, 0.0, 0.0, self.currentZoomFactor, 0, 0))
            
    #        print(self.mapToScene(self.viewport().geometry()).boundingRect())
        else: 
            deltaX = event.angleDelta().x()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + deltaX/2)
            deltaY = event.angleDelta().y()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + deltaY/2)
        self.updatePaintersRectSignal.emit(self.currentZoomFactor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #print("CLICK")
            aa = self.mapToScene(self.viewport().geometry()).boundingRect()
            bb = self.viewport().geometry()
            cc = self.viewport()
            print(f"map2Scene {aa}, \ngeom {bb}, \nviewPort {cc}\n\n\n")
            x = event.x()
            y = event.y()
            print(self.mapToScene(x,y))
            #print(self.geometry())
            #print(self.mapToScene(self.viewport().geometry()).boundingRect())
            #self.addLines()
            #print(self.parent.isMaximized())
            #self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + x)
        elif event.button() == Qt.RightButton:
            #self.setSceneRect(0,0,10000,500)
            #print(self.staffScene.itemsBoundingRect())
            #self.addStaffs()
            #self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() +5000)
            # view->verticalScrollBar()->setValue( view->verticalScrollBar()->value() + dy );
            pass
