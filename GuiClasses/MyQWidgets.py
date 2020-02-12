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

class MyQCheckBox(QCheckBox):
    hit = pyqtSignal(int, bool, object)
    def __init__(self, parent, player):
        super(MyQCheckBox, self).__init__(parent)
        self.parent = parent
        self.player = player
        self.stateChanged.connect(self.sendNewSignal)
    @pyqtSlot(int)
    def sendNewSignal(self, state):
        self.hit.emit(state, self.isChecked(), self.player)
class MyQSpinBox(QSpinBox):
    hit = pyqtSignal(int, object, object)
    def __init__(self, parent, player):
        super(MyQSpinBox, self).__init__(parent)
        self.parent = parent
        self.player = player
        self.valueChanged.connect(self.sendNewSignal)
    @pyqtSlot(int)
    def sendNewSignal(self, value):
        self.hit.emit(value, None, self.player)
class MyQDoubleSpinBox(QDoubleSpinBox):
    hit = pyqtSignal(float, object, object)
    def __init__(self, parent, player):
        super(MyQDoubleSpinBox, self).__init__(parent)
        self.parent = parent
        self.player = player
        self.valueChanged.connect(self.sendNewSignal)
    @pyqtSlot(float)
    def sendNewSignal(self, value):
        self.hit.emit(value, None, self.player)

class MyQComboBox(QComboBox):
    hit = pyqtSignal(int, object, object)
    def __init__(self, parent, player):
        super(MyQComboBox, self).__init__(parent)
        self.parent = parent
        self.player = player
        self.activated.connect(self.sendNewSignal)
    @pyqtSlot(int)
    def sendNewSignal(self, value):
        print(f"skata {value}")
        self.hit.emit(value, None, self.player)