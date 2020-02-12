# pyQt5 imports
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect, QSize
from PyQt5.QtGui import (QPen, QTransform, QIcon)
from PyQt5.QtSvg import QGraphicsSvgItem
class ToolBar(QToolBar):
    def __init__(self, appctxt, params, parent):
        super(ToolBar,self).__init__(parent)
        self.appctxt = appctxt
        self.params = params
        self.setIconSize(QSize(30,30))

        self.playPause = QAction("Play/Pause (Space)",self)
        self.playPause.setShortcut(Qt.Key_Space)
        self.playPause.setShortcutContext(Qt.ApplicationShortcut)
        self.playPause.setIcon(QtGui.QIcon(self.appctxt.get_resource("Images/svg/play.svg")))

        self.reset = QAction("Reset Memory (Ctrl+R)",self)
        self.reset.setShortcut("Ctrl+R")
        self.reset.setShortcutContext(Qt.ApplicationShortcut)
        self.reset.setIcon(QIcon(self.appctxt.get_resource("Images/svg/reset.svg")))

        self.condition = QAction("Condition (Ctrl+C)",self)
        self.condition.setShortcut("Ctrl+C")
        self.condition.setShortcutContext(Qt.ApplicationShortcut)
        self.condition.setIcon(QIcon(self.appctxt.get_resource("Images/svg/upload.svg")))

        self.preferences = QAction("Preferences (Ctrl+P)",self)
        self.preferences.setShortcut("Ctrl+P")
        self.preferences.setShortcutContext(Qt.ApplicationShortcut)
        self.preferences.setIcon(QIcon(self.appctxt.get_resource("Images/svg/settingsBlueBig.svg")))

        self.save = QAction("Save (Ctrl+S)",self)
        self.save.setShortcut("Ctrl+S")
        self.save.setShortcutContext(Qt.ApplicationShortcut)
        self.save.setIcon(QIcon(self.appctxt.get_resource("Images/svg/save.svg")))

        
        self.lcd = QLCDNumber(self)
        self.lcd.display(1)
        self.lcd.setDigitCount(1)
        self.lcd.setFixedHeight(35)
        self.lcd.setFixedWidth(35)
        #sld.valueChanged.connect(self.lineEdit.setText()) 
        # # get the palette
        # palette = self.lcd.palette()
        # # foreground color
        # palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        # # background color
        # palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        # # "light" border
        # palette.setColor(palette.Light, QtGui.QColor(255, 0, 0))
        # # "dark" border
        # palette.setColor(palette.Dark, QtGui.QColor(0, 255, 0))

        # # set the palette
        # self.lcd.setPalette(palette)


        self.bpmBox = QSpinBox(self)
        self.bpmBox.setSuffix(" BPM")
        #self.bpmBox.setMinimumSize(30,30)
        self.bpmBox.setFixedHeight(35)
        self.bpmBox.setRange(20,150)
        self.bpmBox.setSingleStep(5)
        self.bpmBox.setValue(self.params['metronome']["BPM"])

        # self.enforce = QAction("Enforce",self)
        # self.enforce.setShortcut("Ctrl+E")
        # self.enforce.setShortcutContext(Qt.ApplicationShortcut)

        # self.clear = QAction("Clear",self)
        # #self.clear.setShortcut("Ctrl+E")
        # self.clear.setShortcutContext(Qt.ApplicationShortcut)

        #self.enforce.setIcon(QIcon(self.appctxt.get_resource("Images/reset.svg")))
        #self.toolbarAction.setStatusTip("STARTPAUSE")
        #self.toolbarAction.setWhatsThis("srgsr")
        self.addAction(self.playPause)
        self.addAction(self.reset)
        self.addAction(self.condition)
        self.addAction(self.preferences)
        self.addAction(self.save)
        self.addWidget(self.bpmBox)
        self.addWidget(self.lcd)
        self.keyIndicator = QLabel("          ", objectName='keyIndicator')
        #self.addWidget(self.keyIndicator)

        
        # self.randomnessSlider = QSlider(Qt.Horizontal, self)
        # self.randomnessSlider.setRange(1,100)
        # self.randomnessSlider.setSizeIncrement(1,1)
        # self.randomnessSlider.setValue(4)#self.params['metronome']["volume"])
        # self.sliderLabel = QLabel("    ", objectName = 'sliderLabel')
        
        # layout = QGridLayout()
        # layout.addWidget(self.randomnessSlider,0,0,1,1)

        # ss = QWidget()
        # ss.setLayout(layout)
        # self.addWidget(ss)
        
        
        
        # self.addAction(self.enforce)
        # self.addAction(self.clear)