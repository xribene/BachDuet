from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,QMessageBox,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy, QDialogButtonBox,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit, QSplashScreen,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QFormLayout, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform, QPixmap)
from PyQt5.QtSvg import QGraphicsSvgItem
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

class InputDialog(QDialog):
    def __init__(self, parent=None, humanPlayers = 1):
        super().__init__(parent)
        self.textLines = []
        layout = QFormLayout(self)
        for i in range(humanPlayers):
            temp = QLineEdit(self)
            self.textLines.append(temp)
            layout.addRow(f"Full Name {i}", temp)
        self.comments = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout.addRow("Experiment Comments", self.comments)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        output = {}
        for i, line in enumerate(self.textLines):
            output[f'fullName {i+1}'] = line.text()
        output['comments'] = self.comments.text()
        return output

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dialog = InputDialog()
    if dialog.exec():
        print(dialog.getInputs())
    exit(0)
'''
katarxas tha vazei onoma epitheto
imerominia  thn krataw etsi ki alliws
add it to subjects
'''
