from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgWidget

from GuiClasses.StaffItem import *
from GuiClasses.Flag import *
#from GraphicsItems.NoteItem import *
import pickle
import numpy as np
from pathlib import Path
from collections import deque
from utils import Params

class PianoRollPainter(QObject):
    # sendNoteItemToMain = pyqtSignal(QtSvg.QGraphicsSvgItem)
    sendNoteItemToMain = pyqtSignal(list, int)

    def __init__(self, pianoRollView, appctxt):
        super().__init__()
        self.pianoRollView = pianoRollView
        self.appctxt = appctxt
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        
        self.showMidiKeyboardFlag = True
        self.midiPositions = self.config.gui["keyPos"]
        # buffers that keep the past 205 notes for both voices
        # the notes in these buffers are plotted to form the 
        # piano roll view.
        self.busMidiKeyboard = deque(maxlen=205) # TODO
        self.busDnn = deque(maxlen=205) # TODO 

    @pyqtSlot(int,int)       
    def updatePlot(self, dnnNote, keyNote):
        
        print(f"new Dnn Note is {dnnNote} and keyNote {keyNote}")
        self.busDnn.append(dnnNote)
        self.busMidiKeyboard.append(keyNote)
        currentKeyBus = list(self.busMidiKeyboard)
        currentDnnBus = list(self.busDnn)
        currentDnnBus.reverse()
        currentKeyBus.reverse()
        plotDataDnn = []
        plotDataKey = []
        for note in currentKeyBus:
            try:
                if note==0:
                    note=21
                plotDataKey.extend([self.midiPositions[note-21] for i in range(24)])
                plotDataKey.append(18)
            except:
                plotDataKey.extend([18 for i in range(25)])
        data1 = np.array(plotDataKey, dtype = np.float32) # 5835
        for note in currentDnnBus:
            try:
                if note==0:
                    note=21
                plotDataDnn.extend([self.midiPositions[note-21] for i in range(24)])
                plotDataDnn.append(18)
            except:
                plotDataDnn.extend([18 for i in range(25)])
        data2 = np.array(plotDataDnn, dtype = np.float32) # 5835
        data2[data2==18] = np.nan
        data1[data1==18] = np.nan
        # if not self.showMidiKeyboardFlag:
        #     data1[data1!=1] = np.nan
        ss = 450
        #print(np.linspace(ss,ss+len(data1),len(data1)))
        #print(data1)
        # print("INSIDE PLOTTER PIANOROLL")
        # print(f"\n\n data1 {data1}")
        # print(f"\n\n data2 {data2}")


        # TODO https://github.com/pyqtgraph/pyqtgraph/issues/1057
        
        # if pg.Qt.VERSION_INFO.split(' ')[0] in ['PySide2', 'PyQt5']:
        #     con = np.isfinite(data1)
        #     data1[~con] = 0
        #     # pg.plot(data1, title="NaN", connect=np.logical_and(con, np.roll(con, -1)))
        #     self.pianoRollView.plotCurve1.setData(np.linspace(ss,ss+len(data1),len(data1)), data1,connect="finite", pen=pg.mkPen(color=(74, 133, 196),width=4, connect=np.logical_and(con, np.roll(con, -1))))

        # else:
        #     # pg.plot(data1, title="NaN", connect='finite')
        #     self.pianoRollView.plotCurve1.setData(np.linspace(ss,ss+len(data1),len(data1)), data1,connect="finite", pen=pg.mkPen(color=(74, 133, 196),width=4))


        self.pianoRollView.plotCurve1.setData(np.linspace(ss,ss+len(data1),len(data1)), data1,connect="finite", pen=pg.mkPen(color=(74, 133, 196),width=4))
        self.pianoRollView.plotCurve2.setData(np.linspace(ss,ss+len(data2),len(data2)), data2,connect="finite", pen=pg.mkPen(color=(0, 128, 0),width=4))