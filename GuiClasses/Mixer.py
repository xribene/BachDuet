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
class MetronomeSlider(QGroupBox):
    def __init__(self, players, params, parent = None):
        super(MetronomeSlider, self).__init__()
        self.params = params
        self.setTitle("Metronome")
        self.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.muteButton = QPushButton("M", self)
        self.muteButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.muteButton.setCheckable(True)
        self.muteButton.setChecked(False)
        self.muteButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.soloButton = QPushButton("S", self)
        self.soloButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.soloButton.setCheckable(True)
        self.soloButton.setChecked(False)
        self.soloButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0,127)
        self.volumeSlider.setValue(32)#self.params['metronome']["volume"])
        

        # bpmLabel = QLabel("BPM")
        # self.bpmBox = QSpinBox(self)
        # self.bpmBox.setRange(20,150)
        # self.bpmBox.setSingleStep(5)
        # self.bpmBox.setValue(60)
        # bpmLabel.setBuddy(self.bpmBox)
        
        layout = QGridLayout()
        # layout.addWidget(bpmLabel, 0, 0, 1, 1)
        # layout.addWidget(self.bpmBox,0,1,1,1)
        layout.addWidget(self.muteButton, 0, 0, 1, 1)
        layout.addWidget(self.soloButton, 0, 1, 1, 1)
        layout.addWidget(self.volumeSlider, 1, 0, 3, 2, Qt.AlignCenter)
        self.setLayout(layout)
class NeuralNetSlider(QGroupBox):
    def __init__(self, params, parent = None):
        super(NeuralNetSlider, self).__init__()
        self.params = params
        self.setTitle("NeuralNet")
        self.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.muteButton = QPushButton("M", self)
        self.muteButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.muteButton.setCheckable(True)
        self.muteButton.setChecked(False)
        self.muteButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.soloButton = QPushButton("S", self)
        self.soloButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.soloButton.setCheckable(True)
        self.soloButton.setChecked(False)
        self.soloButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0,127)
        self.volumeSlider.setValue(self.params['machine']["volume"])
        
        
        layout = QGridLayout()
        layout.addWidget(self.muteButton, 0, 0, 1, 1)
        layout.addWidget(self.soloButton, 0, 1, 1, 1)
        layout.addWidget(self.volumeSlider, 1, 0, 3, 2, Qt.AlignCenter)
        self.setLayout(layout)
class HumanInputSlider(QGroupBox):
    def __init__(self, params, parent = None):
        super(HumanInputSlider, self).__init__()
        self.params = params
        self.setTitle("Human Input")
        self.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.muteButton = QPushButton("M", self)
        self.muteButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.muteButton.setCheckable(True)
        self.muteButton.setChecked(False)
        self.muteButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.soloButton = QPushButton("S", self)
        self.soloButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.soloButton.setCheckable(True)
        self.soloButton.setChecked(False)
        self.soloButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0,127)
        self.volumeSlider.setValue(self.params['human']["volume"])
        
        
        layout = QGridLayout()
        layout.addWidget(self.muteButton, 0, 0, 1, 1)
        layout.addWidget(self.soloButton, 0, 1, 1, 1)
        layout.addWidget(self.volumeSlider, 1, 0, 3, 2, Qt.AlignCenter)
        self.setLayout(layout)
class MasterSlider(QGroupBox):
    def __init__(self, params, parent = None):
        super(MasterSlider, self).__init__()
        self.params = params
        self.setTitle("Master")
        self.setStyleSheet("QGroupBox { color: green; font: bold;} ")
        self.muteButton = QPushButton("M", self)
        self.muteButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.muteButton.setCheckable(True)
        self.muteButton.setChecked(False)
        self.muteButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.soloButton = QPushButton("S", self)
        self.soloButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.soloButton.setCheckable(True)
        self.soloButton.setChecked(False)
        self.soloButton.setFixedSize(22,22)
        #self.muteButton.pressed.connect(self.)
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0,127)
        self.volumeSlider.setValue(127)
        
        
        layout = QGridLayout()
        layout.addWidget(self.muteButton, 0, 0, 1, 1)
        layout.addWidget(self.soloButton, 0, 1, 1, 1)
        layout.addWidget(self.volumeSlider, 1, 0, 3, 2, Qt.AlignCenter)
        self.setLayout(layout)
class Mixer(QWidget):
    def __init__(self, players, params, appctxt,parent = None):
        super(Mixer, self).__init__(parent)
        self.parent = parent
        self.players = players
        self.params = params
        self.appctxt = appctxt
        self.setWindowIcon(QIcon(self.appctxt.get_resource('Images/svg/mixer.svg')))
        self.installEventFilter(self)
        #self.setWindowFlag(Qt.WindowTransparentForInput)
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.Window)#|Qt.FramelessWindowHint)
        #self.setFocusPolicy( Qt.NoFocus )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.isShown = False
        self.setWindowTitle("Mixer")
        s = QStyleFactory.create('Fusion')
        self.setStyle(s)
        
        #columns = len(self.players)
        mainLayout = QGridLayout(self)
        for i, player in enumerate(self.players):
            if player.type == 'human':
                tempSlider = HumanInputSlider(params,self)
            elif player.type == 'machine':
                tempSlider = NeuralNetSlider(params,self)
            elif player.type == 'metronome':
                tempSlider = MetronomeSlider(params,self)
            elif player.type == 'condition':
                pass # TODO
            player.mixerSlider = tempSlider
            mainLayout.addWidget(tempSlider, 0,i,3,1)
        self.masterSlider = MasterSlider(params, self)
        mainLayout.addWidget(self.masterSlider,  0,i+1,3,1)
        self.setLayout(mainLayout)
    def showWindow(self):
        if self.isShown is True:
            self.isShown = False
            self.hide()
        else:
            self.show()
            self.isShown = True
    def closeEvent(self, event):
        self.isShown = False
        self.parent.menuBar.showMixerAction.setChecked(False)
        pass
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