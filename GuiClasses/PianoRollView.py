from PyQt5 import QtGui
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from PyQt5.QtWidgets import QGraphicsPixmapItem 
from PyQt5 import QtGui
from GuiClasses.StaffItem import *
import pyqtgraph as pg
#from GraphicsItems.NoteItem import *

class PianoRollView(pg.PlotWidget):
    def __init__(self,appctxt, parent):
        super().__init__()
        self.parent = parent
        self.setMouseEnabled(x=True, y=True)
        self.appctxt = appctxt
        
        self.plotCurve1 = pg.PlotCurveItem()
        self.plotCurve2 = pg.PlotCurveItem()
        
        self.getPlotItem().addItem(self.plotCurve1)
        self.getPlotItem().addItem(self.plotCurve2)
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

        image = QtGui.QPixmap(self.appctxt.get_resource('Images/keysBackGrey.png'))
        keysImg = QGraphicsPixmapItem(image)
        keysImg.setZValue(-100)

        self.invertX(True)
        self.addItem(keysImg)  

    
   