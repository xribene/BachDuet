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
import numpy as np
class StaffLine(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, thickness, visible, color, parent):
        super().__init__(x1,y1,x2,y2,parent)
        pen = QPen()
        pen.setWidth(1)
        if  color is None:
            pen.setBrush(Qt.green)
        else:
            pen.setBrush(color)
        #self.setBrush(Qt.white)
        self.setPen(pen)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setVisible(visible)
class Staff(QGraphicsItemGroup):
    def __init__(self, boundingRect, parent=None):
        super().__init__(parent)
        # self.disk1 = MyDisk(50, 50, 20, Qt.red)
        # self.disk2 = MyDisk(150, 150, 20, Qt.red)
        # self.addToGroup(self.disk1)
        # self.addToGroup(self.disk2)
        linesPerStaff = 5
        visibleStaffsNumber = 2
        invisibleStaffsNumber = visibleStaffsNumber * 2 - 1 + 1
        totalStaffs = visibleStaffsNumber + invisibleStaffsNumber
        self.totalLines = linesPerStaff * (visibleStaffsNumber + invisibleStaffsNumber)
        staffVisibility = []
        [staffVisibility.extend([0,1,0]) for i in range(visibleStaffsNumber)]
        staffVisibility = [0,0,1,0,1,0]
        [xStart, yStart, height, width] = [boundingRect.x(), boundingRect.y(), boundingRect.height(), boundingRect.width()]
        print(f"height in staffLines {height} {width}")
        # print(f"Height is {height}")
        # Find line positions
        # We have 2 real staffs and 4 imaginary. I R I I R I. 
        ###################### HORIZONTAL LINES #########################
        self.lineDistance = (height/(self.totalLines+1))
        i = 0
        linePositions = []
        temp = []
        colors = [Qt.green, Qt.red ]
        for staff in range(totalStaffs):
            for line in range(linesPerStaff):
                temp.append(i)
                i += self.lineDistance
            linePositions.append(temp)
            temp = []
        lines = []
        for staff in range(totalStaffs):
            lines.extend([StaffLine(0,pos,100000000,pos, 2, staffVisibility[staff], Qt.black, self) for pos in linePositions[staff]])
        [self.addToGroup(line) for line in lines]
        #
        self.sopranoStaffLinePos = linePositions[2]
        self.bassoStaffLinePos = linePositions[4]
        ####################### VERTICAL LINES ##########################
        ## vertical lines for grid
        # tha swsw ola ta horizontal positions
        totalSymbolSlots = int(np.floor(width/self.lineDistance))
        totalNoteSlots = int(np.floor(totalSymbolSlots/3) -3) # each note has 3 slots (acc-note-malakia) - 3 slots for clef
        horPoint = 7 * self.lineDistance # to vazw sto 4, kai tha pigainw kai tha vazw acc sto -1. Ektos an ftia3w notes me ensomatomeni acc opote tha ginei 3*lineDistance
        self.horNotePositions = []
        for i in range(totalNoteSlots):
            self.horNotePositions.append(horPoint)
            horPoint += 3*self.lineDistance
              