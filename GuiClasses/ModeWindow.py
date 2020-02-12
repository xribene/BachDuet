from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,QDesktopWidget,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton,QButtonGroup, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform, QIcon)
from PyQt5.QtSvg import QGraphicsSvgItem

class ModeWindow(QWidget):
    def __init__(self, appctxt, parent = None):
        super(ModeWindow, self).__init__(parent)
        self.setObjectName("ModeWindow")
        self.parent = parent
        self.appctxt = appctxt
        #self.setWindowIcon(QIcon(self.appctxt.get_resource('Images/mixer.svg')))
        #self.installEventFilter(self)

        self.setGeometry(QtCore.QRect(30, 240, 305, 105))
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        #self.setWindowFlag(Qt.WindowTransparentForInput)
        #self.setFocusPolicy( Qt.NoFocus )
        #self.setAttribute(Qt.WA_ShowWithoutActivating )
        # self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setStyleSheet("QWidget#ModeWindow {background:rgba(235, 205, 34, 0.349);}")
        self.setWindowOpacity(0.95)
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.isShown = False
        self.setWindowTitle("Select Players")
        s = QStyleFactory.create('Fusion')
        self.setStyle(s)
        
        self.buttonGroup = QButtonGroup()
        #
        self.humanVsMachine = QPushButton("Human VS Machine",self)
        self.machineVsMachine = QPushButton("Machine VS Machine",self)
        self.humanVsHuman = QPushButton("Human VS Human",self)
        self.buttonGroup.addButton(self.humanVsMachine, 0)
        self.humanVsMachine.setObjectName("hm")
        self.machineVsMachine.setObjectName("mm")
        self.humanVsHuman.setObjectName("hh")
        self.buttonGroup.addButton(self.machineVsMachine, 1)
        self.buttonGroup.addButton(self.humanVsHuman, 2)
        mainLayout = QGridLayout(self)
        mainLayout.addWidget(self.humanVsMachine, 0,0,1,1)
        mainLayout.addWidget(self.machineVsMachine,  1,0,1,1)
        mainLayout.addWidget(self.humanVsHuman,  2,0,1,1)
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
        #self.parent.menuBar.showMixerAction.setChecked(False)
        pass
    # def eventFilter(self, object, event):
    #     if event.type() == QtCore.QEvent.KeyPress:
    #         print("MIDIKADI")
    #         self.parent.eventFilter(object, event)
    #         #event.ignore()
    #     return False
    # def keyPressEvent(self, eventQKeyEvent):
    #     key = eventQKeyEvent.key()
    #     self.parent.keyPressEvent(eventQKeyEvent)
    # def keyReleaseEvent(self, eventQKeyEvent):
    #     key = eventQKeyEvent.key()
    #     self.parent.keyReleaseEvent(eventQKeyEvent)