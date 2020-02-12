from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5.QtSvg import QGraphicsSvgItem

class MenuBar(QMenuBar):
    def __init__(self, parent = None):
        super(MenuBar, self).__init__(parent)

        fileMenu = self.addMenu ("File")
        #editMenu = self.addMenu ("Edit")
        viewMenu = self.addMenu("View")
        helpMenu = self.addMenu("Help")
        # File actions
        importAction = QAction("Import",self)
        saveAction =  QAction("Save",self)
        saveAction.setShortcut("Ctrl+S")
        self.quitAction =  QAction("Quit",self)
        self.quitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(importAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(self.quitAction)
        # importAction.triggered.connect(self.importWidget.showWindow)
        # saveAction.triggered.connect(self.saveWidget.showWindow)
        # edit Actions
        # connectionsAction = QAction("Connections", self)
        # self.preferencesAction =  QAction("Preferences",self)
        # self.preferencesAction.setShortcutContext(Qt.ApplicationShortcut)
        # editMenu.addAction(connectionsAction)
        # editMenu.addAction(self.preferencesAction)
        # connectionsAction.triggered.connect(self.connectionsWidget.showWindow)
        # preferencesAction.triggered.connect(self.preferencesWidget.showWindow)

        # View Actions
        self.showMixerAction = QAction("Mixer", self)
        self.showMixerAction.setShortcut("F3")
        self.showMixerAction.setShortcutContext(Qt.ApplicationShortcut )

        showPianoRollAction =  QAction("Piano Roll",self)
        showStaffAction =  QAction("Staffs",self)

        showPianoRollAction.setCheckable(True)
        showPianoRollAction.setChecked(True)
        showStaffAction.setCheckable(True)
        showStaffAction.setChecked(True)
        self.showMixerAction.setCheckable(True)
        self.showMixerAction.setChecked(False)

        viewMenu.addAction(self.showMixerAction)
        viewMenu.addAction(showPianoRollAction)
        viewMenu.addAction(showStaffAction)
        
        #showPianoRollAction.triggered.connect(self.updatePianoRollShowFlag)
        # Help Actions
        self.instructionsAction = QAction("&Instructions", self)
        self.instructionsAction.setShortcut("F1")
        self.aboutAction =  QAction("&About",self)
        self.aboutQtAction =  QAction("&About Qt",self)
        helpMenu.addAction(self.instructionsAction)
        helpMenu.addAction(self.aboutAction)
        helpMenu.addAction(self.aboutQtAction)

        self.show()