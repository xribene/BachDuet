# pyQt5 imports
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,QToolButton,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform, QIcon)
from PyQt5.QtSvg import QGraphicsSvgItem
from GuiClasses.MyQWidgets import *
import logging
class InputOutputTab(QGroupBox):
    def __init__(self, params, parent = None):
        super(InputOutputTab, self).__init__("",parent)
        self.appctxt = parent.parent.appctxt
        
        self.midiInBox = QComboBox(self)
        #self.midiInBox.addItems(parent.parent.midiInDict.keys())
        midiInLabel = QLabel("Midi In Port")
        midiInLabel.setBuddy(self.midiInBox)

        

        self.midiOutBox = QComboBox(self)
        #self.midiOutBox.addItems(parent.parent.midiOutDict.keys())
        midiOutLabel = QLabel("Midi Out Port")
        midiOutLabel.setBuddy(self.midiOutBox)

        self.refreshMidiButton = QPushButton("", self)
        # self.refreshMidiButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
        # left  ->setToolButtonStyle(Qt::ToolButtonTextOnly);
        # self.refreshMidiButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.refreshMidiButton.setObjectName("refreshMidi")
        self.refreshMidiButton.setIcon(QIcon(self.appctxt.get_resource('Images/svg/midiRefresh.svg')))
        

        layout = QGridLayout()
        refreshLayout = QGridLayout()
        refreshLayout.addWidget(self.refreshMidiButton, 0,0,1,1)

        layout.addWidget(midiInLabel, 0, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiInBox,0,1,1,1, Qt.AlignCenter)
        layout.addWidget(midiOutLabel, 1, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiOutBox, 1, 1, 1, 1, Qt.AlignCenter)
        # layout.addWidget(refreshLayout, 0,2,1,2, Qt.AlignCenter)
        layout.addWidget(self.refreshMidiButton, 0,2,2,1, Qt.AlignLeft)
        # layout.setColumnMinimumWidth(0, 50) 
        layout.setColumnMinimumWidth(1, 30)
        # layout.setRowMinimumHeight(0, 20) 
        # layout.setRowMinimumHeight(1, 20) 
        
        #layout.setRowStretch(5, 1)
        self.setLayout(layout)
class MachineTab(QGroupBox):
    def __init__(self, params, player, parent = None):
        super(MachineTab, self).__init__("Machine",parent)
        # self.neuralNetGroup = QGroupBox("Neural Network")
        # self.neuralNetGroup.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.appctxt = parent.parent.appctxt
        self.isShown = False
        

        channelOutLabel = QLabel("Midi Out Channel")
        self.channelOutBox = MyQSpinBox(self, player)
        self.channelOutBox.setRange(1,16)
        self.channelOutBox.setSingleStep(1)
        self.channelOutBox.setValue(params['machine']["midiChanOut"])
        channelOutLabel.setBuddy(self.channelOutBox)

        tempLabel = QLabel("Sampling Temp.")
        self.tempBox = MyQDoubleSpinBox(self, player)
        self.tempBox.setRange(0.05,2.0)
        self.tempBox.setSingleStep(0.05)
        self.tempBox.setValue(params['machine']["temperature"])
        tempLabel.setBuddy(self.tempBox)
        

        self.modelsComboBox = MyQComboBox(self, player)
        self.modelsComboBox.addItems(['LSTM','dilated CNN'])
        modelsLabel = QLabel("Model")
        modelsLabel.setBuddy(self.modelsComboBox)

        self.midiOutBox = MyQComboBox(self, player)
        #self.midiOutBox.addItems(parent.parent.midiOutDict.keys())
        midiOutLabel = QLabel("Midi Out Port")
        midiOutLabel.setBuddy(self.midiOutBox)
        self.refreshMidiButton = QPushButton("", self)
        self.refreshMidiButton.setObjectName("refreshMidi")
        self.refreshMidiButton.setIcon(QIcon(self.appctxt.get_resource('Images/svg/midiRefresh.svg')))

        layout = QGridLayout()
        layout.addWidget(modelsLabel, 0, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.modelsComboBox,0,1,1,1, Qt.AlignCenter)
        layout.addWidget(tempLabel, 1, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.tempBox, 1, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(channelOutLabel, 2, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.channelOutBox, 2, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(midiOutLabel, 3, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiOutBox, 3, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.refreshMidiButton, 4, 1, 1, 1, Qt.AlignCenter)
        #layout.setRowStretch(5, 1)
        self.setLayout(layout)

class HumanInputTab(QGroupBox):
    def __init__(self, params, player, parent = None):
        super(HumanInputTab, self).__init__("Human",parent)
        self.appctxt = parent.parent.appctxt
        type = player.type
        # self.neuralNetGroup = QGroupBox("Neural Network")
        # self.neuralNetGroup.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.isShown = False
        
        directMonLabel = QLabel("Direct Monitoring")
        self.directMonBox = MyQCheckBox(self, player)
        # self.directMonBox.stateChanged.connect(self.directMonBox.sendNewSignal)
        self.directMonBox.setChecked(params['human']["directMon"])
        directMonLabel.setBuddy(self.directMonBox)

        queueMidiEventsLabel = QLabel("Queueing Midi Events")
        self.queueMidiEventsBox = MyQCheckBox(self, player)
        self.queueMidiEventsBox.setChecked(params[type]["queueEvents"])
        queueMidiEventsLabel.setBuddy(self.queueMidiEventsBox)

        keyboardInpLabel = QLabel("Enable Keyboard Input")
        self.keyboardInpBox = MyQCheckBox(self, player)
        self.keyboardInpBox.setChecked(params[type]["internalKeyboard"])
        keyboardInpLabel.setBuddy(self.keyboardInpBox)

        channelInLabel = QLabel("Midi In Channel")
        self.channelInBox = MyQSpinBox(self, player)
        self.channelInBox.setRange(1,16)
        self.channelInBox.setSingleStep(1)
        self.channelInBox.setValue(params[type]["midiChanIn"])
        channelInLabel.setBuddy(self.channelInBox)

        channelOutLabel = QLabel("Midi Out Channel")
        self.channelOutBox = MyQSpinBox(self, player)
        self.channelOutBox.setRange(1,16)
        self.channelOutBox.setSingleStep(1)
        self.channelOutBox.setValue(params[type]["midiChanOut"])
        channelOutLabel.setBuddy(self.channelOutBox)

        self.midiInBox =  MyQComboBox(self, player)
        #self.midiOutBox.addItems(parent.parent.midiOutDict.keys())
        midiInLabel = QLabel("Midi In Port")
        midiInLabel.setBuddy(self.midiInBox)

        self.midiOutBox =  MyQComboBox(self, player)
        #self.midiOutBox.addItems(parent.parent.midiOutDict.keys())
        midiOutLabel = QLabel("Midi Out Port")
        midiOutLabel.setBuddy(self.midiOutBox)
        self.refreshMidiButton = QPushButton("", self)
        self.refreshMidiButton.setObjectName("refreshMidi")
        self.refreshMidiButton.setIcon(QIcon(self.appctxt.get_resource('Images/svg/midiRefresh.svg')))


        layout = QGridLayout()
        layout.addWidget(queueMidiEventsLabel, 0, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.queueMidiEventsBox,0,1,1,1, Qt.AlignCenter)
        layout.addWidget(directMonLabel, 1, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.directMonBox,1,1,1,1, Qt.AlignCenter)
        layout.addWidget(keyboardInpLabel, 2, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.keyboardInpBox, 2, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(channelInLabel, 3, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.channelInBox, 3, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(channelOutLabel, 4, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.channelOutBox, 4, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(midiInLabel, 5, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiInBox, 5, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.refreshMidiButton, 6, 0, 1, 2, Qt.AlignCenter)
        layout.addWidget(midiOutLabel, 7, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiOutBox, 7, 1, 1, 1, Qt.AlignCenter)

        #layout.setRowStretch(5, 1)
        self.setLayout(layout)
class MetronomeTab(QGroupBox):
    def __init__(self, params, player, parent = None):
        super(MetronomeTab, self).__init__("Metronome",parent)
        self.appctxt = parent.parent.appctxt
        #self.metronomeGroup = QGroupBox("Metronome")
        channelOutLabel = QLabel("Midi Out Channel")
        self.channelOutBox = MyQSpinBox(self, player)
        self.channelOutBox.setRange(1,16)
        self.channelOutBox.setSingleStep(1)
        self.channelOutBox.setValue(params['metronome']["midiChanOut"])
        channelOutLabel.setBuddy(self.channelOutBox)

        firstPitch = QLabel("First Beat Pitch")
        self.firstPitchBox = MyQSpinBox(self, player)
        self.firstPitchBox.setRange(0,127)
        self.firstPitchBox.setSingleStep(1)
        self.firstPitchBox.setValue(params['metronome']["pitch1"])
        firstPitch.setBuddy(self.firstPitchBox)

        otherPitch = QLabel("Other Beats Pitch")
        self.otherPitchBox = MyQSpinBox(self, player)
        self.otherPitchBox.setRange(0,127)
        self.otherPitchBox.setSingleStep(1)
        self.otherPitchBox.setValue(params['metronome']["pitch2"])
        otherPitch.setBuddy(self.otherPitchBox)
        
        self.midiOutBox =  MyQComboBox(self, player)
        #self.midiOutBox.addItems(parent.parent.midiOutDict.keys())
        midiOutLabel = QLabel("Midi Out Port")
        midiOutLabel.setBuddy(self.midiOutBox)
        self.refreshMidiButton = QPushButton("", self)
        self.refreshMidiButton.setObjectName("refreshMidi")
        self.refreshMidiButton.setIcon(QIcon(self.appctxt.get_resource('Images/svg/midiRefresh.svg')))

        layout = QGridLayout()
        layout.addWidget(firstPitch, 0, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.firstPitchBox,0,1,1,1, Qt.AlignCenter)
        layout.addWidget(otherPitch, 1, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.otherPitchBox, 1, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(channelOutLabel, 2, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.channelOutBox, 2, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(midiOutLabel, 3, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.midiOutBox, 3, 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.refreshMidiButton, 4, 1, 1, 1, Qt.AlignCenter)
        self.setLayout(layout)
class Preferences(QWidget):
    def __init__(self, players, params, appctxt, parent = None):
        super(Preferences, self).__init__(parent)
        self.appctxt = appctxt
        self.players = players
        self.params = params
        self.parent = parent
        # style / geometry
        self.setWindowTitle('Preferences')
        s = QStyleFactory.create('Fusion')
        self.setWindowIcon(QIcon(self.appctxt.get_resource('Images/svg/settingsBlueBig.svg')))
        #self.setMinimumSize(500,200)
        self.setStyle(s)
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.Window)#|Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.isShown = False
        #
        self.installEventFilter(self)
        self.tabs = QTabWidget(self)
        self.tabs.setFixedSize(400,300)
        #self.inputOutputTab =InputOutputTab(params,self)
        #self.tabs.addTab(self.inputOutputTab, 'Input/Output')
        for player in self.players:
            if player.type in [ 'human', 'human2']:
                tempTab = HumanInputTab(params,player, self)
                player.preferencesTab = tempTab
            elif player.type in [ 'machine', 'machine2']:
                tempTab = MachineTab(params,player, self)
                player.preferencesTab = tempTab
            elif player.type == 'metronome':
                tempTab = MetronomeTab(params,player, self)
                player.preferencesTab = tempTab
            elif player.type == 'condition':
                pass # TODO
            # player.preferencesTab = tempTab
            self.tabs.addTab(tempTab, f"{player.name} ({player.type})")
        # self.neuralNetTab = MachineTab(params,self)
        # #self.tabs.addTab(self.neuralNetTab, "Neural Net")
        # self.metronomeTab = MetronomeTab(params,self)
        # self.humanInputTab = HumanInput(params,self)
        # self.inputOutputTab =InputOutputTab(params,self)
        

        #self.layout = QGridLayout(self)
        # self.layout.addWidget(self.humanInputTab, 1,0,1,1)
        # self.layout.addWidget(self.neuralNetTab, 1,1,1,1)
        # self.layout.addWidget(self.metronomeTab, 0,1,1,1)
        # self.layout.addWidget(self.inputOutputTab, 0,0,1,1)
        #self.setLayout(self.layout)
        #self.showWindow()

    def showWindow(self):
        print("PAPAPAPAPAPAPAPAPAPAPAPAPAPPPPPPPPPPPPPPPPPPPPP")
        if self.isShown is True:
            self.isShown = False
            self.hide()
            #self.neuralNetTab.hide()
        else:
            self.show()
            #self.neuralNetTab.show()
            self.isShown = True
    def closeEvent(self, event):
        self.isShown = False
        pass
    # # def eventFilter(self, object, event):
    # #     if event.type() == QtCore.QEvent.KeyPress:
    # #         print("MIDIKADI")
    # #         self.parent.eventFilter(object, event)
    # #         #event.ignore()
    # #     return False
    # def keyPressEvent(self, eventQKeyEvent):
    #     print("[ress")
    #     key = eventQKeyEvent.key()
    #     self.parent.keyPressEvent(eventQKeyEvent)
    # def keyReleaseEvent(self, eventQKeyEvent):
    #     print("release")
    #     key = eventQKeyEvent.key()
    #     self.parent.keyReleaseEvent(eventQKeyEvent)
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress:
            print("MIDIKADI")
            self.parent.eventFilter(object, event)
            #event.ignore()
        return False
    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        self.parent.keyPressEvent(eventQKeyEvent)
    def keyReleaseEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        self.parent.keyReleaseEvent(eventQKeyEvent)
