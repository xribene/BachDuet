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

class Flag(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head,appctxt, parent = None):  
        if dur == 1:
            filePath = appctxt.get_resource(str(svgFolder / "flag16.svg"))
            #print(self.filePath)
            heightRel = 3.5
            widthRel = 1
            vertOff = -heightRel + 1/2
            horOff = head.widthRel -1/5
        elif dur in [2,3]:
            filePath = appctxt.get_resource(str(svgFolder / "flag8.svg"))
            heightRel = 3
            widthRel = 1
            vertOff = -heightRel 
            horOff = head.widthRel  -1/8
        else:
            filePath = None
        #filePath = None
        if filePath is not None:
            super(Flag, self).__init__(filePath, parent)
        else: 
            super(Flag, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff*self.lineDistance , vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
class Head(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, appctxt,parent = None):  
        if dur in [1,2,3,4,6]:
            filePath = appctxt.get_resource(str(svgFolder / "noteFilled.svg"))
            #print(self.filePath)
            heightRel = 1
            widthRel = 1.2
        elif dur in [8,12]:
            filePath = appctxt.get_resource(str(svgFolder / "noteHalf.svg"))
            heightRel = 1.12
            widthRel = 1.3
        elif dur  in [16,24]:
            filePath = appctxt.get_resource(str(svgFolder / "noteWhole.svg"))
            heightRel = 1
            widthRel = 2
        else:
            filePath = None
    
        if filePath is not None:
            super(Head, self).__init__(filePath, parent)
        else: 
            super(Head, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos, vertPos)
            self.rightMostPoint = horPos + self.widthReal
            print(f"{horPos} {vertPos} {self.widthScale}")
            # if tieToPrev:
            #     self.set
class Stem(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent): 
        if dur <16:
            filePath = appctxt.get_resource(str(svgFolder / "stem.svg"))
            widthRel = 1/5
            heightRel = 3.5
            horOff = head.widthRel - 1/5
            vertOff = -heightRel + 1/2
        else:
            filePath = None
    
        if filePath is not None:
            super(Stem, self).__init__(filePath, parent)
        else: 
            super(Stem, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:   
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + self.lineDistance * horOff, vertPos + self.lineDistance * vertOff)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
            #self.rect = QRectF(-self.widthReal, - self.heihtReal, self.widthReal, self.heightReal)
        
class Accidental(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine,appctxt, parent): 
        if acc == -1:
            filePath = appctxt.get_resource(str(svgFolder / "accFlat.svg"))
            widthRel = 1
            heightRel = 2.5
            vertOff = - heightRel + 1 + 1/5
            horOff = -1
        elif acc == 1:
            filePath = appctxt.get_resource(str(svgFolder / "accSharp.svg"))
            widthRel = 1
            heightRel = 3
            vertOff = - heightRel/2 + 1/2
            horOff = -1
        else :
            filePath = None
        if filePath is not None:
            super(Accidental, self).__init__(filePath, parent)
        else: 
            super(Accidental, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff*self.lineDistance, vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
            #self.rect = QRectF(-self.widthReal, - self.heihtReal, self.widthReal, self.heightReal)
class Dot(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head,appctxt, parent): 
        if dur in [3,6,12,24]:
            filePath = appctxt.get_resource(str(svgFolder / "dot.svg"))
            widthRel = 4/10
            heightRel = 4/10
            vertOff = 0.1
            horOff = head.widthRel + 0.2
        else :
            filePath = None
        if filePath is not None:
            super(Dot, self).__init__(filePath, parent)
        else: 
            super(Dot, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff * self.lineDistance, vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
            #self.rect = QRectF(-self.widthReal, - self.heihtReal, self.widthReal, self.heightReal)
class Barline(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt, parent): 
        vertPos = vertPosLookUp[0]
        if addBarLine == 1:
            filePath = appctxt.get_resource(str(svgFolder / "barLineSingle.svg"))
            widthRel = 1/6
            heightRel = 14
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 3*(dur-1) + 2 - widthRel/2
        elif addBarLine == 2:
            filePath = appctxt.get_resource(str(svgFolder / "barLineDouble.svg"))
            widthRel = 1
            heightRel = 14
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 3*(dur-1) + 2 - widthRel/2 + 1/2
        else :
            filePath = None
        if filePath is not None:
            super(Barline, self).__init__(filePath, parent)
        else: 
            super(Barline, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff * self.lineDistance, vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal #+ self.lineDistance
            #self.rect = QRectF(-self.widthReal, - self.heihtReal, self.widthReal, self.heightReal)
class Tie(QGraphicsSvgItem):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, lastNoteHorPos, vertPos, addBarLine, head,appctxt, parent): 
        if tieToPrev == 1:
            filePath = appctxt.get_resource(str(svgFolder / "tie.svg"))
            widthRel = (horPos - lastNoteHorPos)/lineDistance
            heightRel = 1
            vertOff = 1.3 #vertPosLookUp[0] - vertPos
            horOff = - (horPos - lastNoteHorPos)/lineDistance + 1/2
        else :
            filePath = None
        if filePath is not None:
            super(Tie, self).__init__(filePath, parent)
        else: 
            super(Tie, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            if invert == 1:
                self.setTransform(QTransform(-1,0,0,-1, self.widthReal, self.heightReal))
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff * self.lineDistance, vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
            #self.rect = QRectF(-self.widthReal, - self.heihtReal, self.widthReal, self.heightReal)
class ExtraLine(QGraphicsSvgItem):
    def __init__(self, horPos, vertPos, head, lineDistance, svgFolder, appctxt,parent): 
        filePath = appctxt.get_resource(str(svgFolder / "extraLine.svg"))
        heightRel = 1/6
        widthRel = 1.35 * head.widthRel
        vertOff = 0 #vertPosLookUp[0] - vertPos
        horOff = -0.25 * head.widthRel / 2
        super(ExtraLine, self).__init__(filePath, parent)
        self.widthRel = widthRel
        self.heightRel = heightRel # na to ypologisw akrivws
        self.lineDistance = lineDistance
        self.heightBefore = self.boundingRect().height()
        self.widthBefore = self.boundingRect().width()
        self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
        self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
        self.widthReal = self.widthRel * self.lineDistance
        self.heightReal = self.heightRel * self.lineDistance
        self.scale(self.widthScale, self.heightScale)
        self.setPos(horPos + horOff * self.lineDistance, vertPos + vertOff * self.lineDistance)
        self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
class ExtraLines(QGraphicsItemGroup):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent): 
        super(ExtraLines, self).__init__(parent)
        # lines above
        self.isNone = True
        for i in range(extraLines[0]):
            tempVertPos = vertPosLookUp[0] - (i+1)*lineDistance
            tempLine = ExtraLine(horPos, tempVertPos, head,  lineDistance, svgFolder, appctxt,self)
            self.addToGroup(tempLine)
        for i in range(extraLines[1]):
            tempVertPos = vertPosLookUp[3] + (2+i)*lineDistance
            tempLine = ExtraLine(horPos, tempVertPos, head,  lineDistance, svgFolder, appctxt,self)
            self.addToGroup(tempLine)
        if sum(extraLines)>0:
            self.isNone = False
            self.rightMostPoint = tempLine.rightMostPoint
class Rest(QGraphicsSvgItem):
    def __init__(self, dur, svgFolder, horPos, vertPosLookUp, lineDistance, appctxt,parent):
        if dur == 1:
            filePath = appctxt.get_resource(str(svgFolder / "rest16.svg"))
            vertPos = vertPosLookUp[2]
            widthRel = 1
            heightRel = 2
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 0
        elif dur in [2,3]:
            filePath = appctxt.get_resource(str(svgFolder / "rest8.svg"))
            vertPos = vertPosLookUp[2]
            widthRel = 1
            heightRel = 2
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 0
        elif dur in [4,6]:
            filePath = appctxt.get_resource(str(svgFolder / "rest4.svg"))
            vertPos = vertPosLookUp[1]
            widthRel = 1
            heightRel = 3
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 0
        elif dur in [8,12]:
            filePath = appctxt.get_resource(str(svgFolder / "restLine.svg"))
            vertPos = vertPosLookUp[1]
            widthRel = 1.5
            heightRel = 1/3
            vertOff = 0 #vertPosLookUp[0] - vertPos
            horOff = 0
        elif dur in [16,24]:
            filePath = appctxt.get_resource(str(svgFolder / "restLine.svg"))
            vertPos = vertPosLookUp[2]
            widthRel = 1.5
            heightRel = 1/3
            vertOff = -1/3 #vertPosLookUp[0] - vertPos
            horOff = 0
        else :
            filePath = None
        if filePath is not None:
            super(Rest, self).__init__(filePath, parent)
        else: 
            super(Rest, self).__init__()
        self.isNone = True if filePath is None else False
        if self.isNone is False:  
            #self.rect = QRectF(0, 0, self.widthReal, self.heightReal)    
            self.widthRel = widthRel
            self.heightRel = heightRel # na to ypologisw akrivws
            self.lineDistance = lineDistance
            self.dur = dur
            self.heightBefore = self.boundingRect().height()
            self.widthBefore = self.boundingRect().width()
            self.widthScale = self.widthRel * self.lineDistance / self.widthBefore
            self.heightScale = self.heightRel * self.lineDistance / self.heightBefore
            self.widthReal = self.widthRel * self.lineDistance
            self.heightReal = self.heightRel * self.lineDistance
            self.scale(self.widthScale, self.heightScale)
            #print(f"{horPos} {vertPos}")
            # self.setPos(horPos + self.lineDistance - self.widthReal, vertPos - self.heightReal + self.lineDistance/2) # 
            ########self.setPos(horPos, vertPos + self.lineDistance/2)
            #print(f" before {self.heightBefore} real {self.heightReal} vertPos {vertPos}")
            self.setPos(horPos + horOff * self.lineDistance, vertPos + vertOff * self.lineDistance)
            self.rightMostPoint = horPos + horOff * self.lineDistance + self.widthReal
class Note(QGraphicsItemGroup):
    def __init__(self, midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, lastNoteHorPos, vertPos, addBarLine, appctxt, parent = None): 
        super(Note, self).__init__(parent)
        itemsForGroup = []
        if midiNumber != 0 :
            head = Head( midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                            svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, appctxt, parent = self)
            stem = Stem( midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt, parent = self)
            flag = Flag( midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent = self)
            acc = Accidental(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, appctxt,parent = self)
            dot = Dot(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent = self)
            barline =Barline(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent = self)
            tie =Tie(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, lastNoteHorPos ,vertPos, addBarLine, head,appctxt, parent = self)
            extraLines =ExtraLines(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, head, appctxt,parent = self)
            itemsForGroup.extend([head, stem, flag, acc, dot, barline, tie, extraLines])
            [self.addToGroup(item) for item in itemsForGroup if item.isNone is False]
            self.rightMostPoint = max([item.rightMostPoint for item in itemsForGroup if item.isNone is False])
        elif midiNumber == 0:
            rest = Rest(dur, svgFolder, horPos, vertPosLookUp, lineDistance, appctxt, parent = self)
            barline =Barline(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, rest, appctxt, parent = self)
            dot = Dot(midiNumber, dur , acc , tieToPrev , vertPosLookUp , extraLines,
                        svgFolder, lineDistance, invert , horPos, vertPos, addBarLine, rest, appctxt, parent = self)
            itemsForGroup.extend([rest, dot, barline])
            [self.addToGroup(item) for item in itemsForGroup if item.isNone is False]
            self.rightMostPoint = max([item.rightMostPoint for item in itemsForGroup if item.isNone is False])
        #print(f"horPos {horPos} d {lineDistance} head {head.rightMostPoint} acc {acc.rightMostPoint} dot {dot.rightMostPoint}")

