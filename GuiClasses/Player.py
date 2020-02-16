# pyQt5 imports
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform, QIcon)
from PyQt5.QtSvg import QGraphicsSvgItem

        
class Player(object):
    """ Player/agent class

    Each player is associated with a Player() class,
    which containes all the important attributes for 
    the player. 

    Attributes:
        id:
        name:
        type:
        params:
        realTimeInput:
        modules:
        managerFlag:
        bpm:
        pitch1:
        pitch2:
        model:
        temperature:
        channelOut:
        channelIn:
        queueMidiEvents:
        directMonFlag:
        internalKeyboardFlag
        volume
        enableMidiKeyboard:
        lastNote:
        nextNote:
        nextNoteDict
        lastMidiEvent:
        lastEvent:
        onRest
        muteStatus
        ignoreNoteOff
        preferenceTab:
        mixerSlider:
        midiIn:
        midiOut:
        defaultMidiIn:
        defaultMidiOut:
    """
    def __init__(self, type, params, realTimeInput, inputType, holdFlag, modules, enableMidiKeyb = True, name = None):
        
        self.id = id(self)
        self.name = name or params[type]['name']
        self.type = type
        self.params = params
        self.realTimeInput = realTimeInput
        self.inputType = inputType
        self.modules = modules
        self.holdFlag = holdFlag
        self.managerFlag = False
        self.bpm = params[type]['BPM']
        self.pitch1 = params[type]['pitch1']
        self.pitch2 = params[type]['pitch2']
        self.model = params[type]['model']
        self.temperature = params[type]['temperature']
        self.channelOut = 144 + params[type]["midiChanOut"] - 1
        if params[type]["midiChanIn"] is not  None:
            self.channelIn = 144 + params[type]["midiChanIn"] - 1
        else :
            self.channelIn = None
        self.queueMidiEvents = params[type]["queueEvents"]
        self.directMonFlag = params[type]["directMon"]
        self.internalKeyboardFlag = params[type]["internalKeyboard"] 
        self.volume = params[type]['volume']
        self.enableMidiKeyb = enableMidiKeyb
        self.lastNote = 0
        self.nextNote = [0,0,0,0,0]
        self.nextNoteDict = {}
        self.lastMidiEvent = [self.channelOut, 0, 0]
        self.lastEvent = {'type':'noteOff',
                          'timestamp':0,
                          'note':0}
        self.onRest = True
        self.muteStatus = False
        self.ignoreNoteOff = 0
        #preferences
        self.preferenceTab = None
        #mixer
        self.mixerSlider = None
        self.meanMidi = 0
        self.midiIn = None
        self.midiOut = None
        self.defaultMidiOut = params[type]["defaultMidiOut"]
        self.defaultMidiIn = params[type]["defaultMidiIn"]

    
