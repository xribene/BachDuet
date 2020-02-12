class PlotWidget2(pg.PlotWidget):
    def __init__(self, parent = None):
        pg.PlotWidget.__init__(self, parent = parent)
        self.mouseEnabled = False
    def mouseMoveEvent(self, ev):
        
        if self.lastMousePos is None:
            self.lastMousePos = pg.Point(ev.pos())
        delta =  pg.Point(ev.pos() - self.lastMousePos)
        self.lastMousePos =  pg.Point(ev.pos())

        QtGui.QGraphicsView.mouseMoveEvent(self, ev)
        if not self.mouseEnabled:
            return
        self.sigSceneMouseMoved.emit(self.mapToScene(ev.pos()))
            
        if self.clickAccepted:  ## Ignore event if an item in the scene has already claimed it.
            return
        
        if ev.buttons() == QtCore.Qt.RightButton:
            print("SRGSRGSRGSRGSRGSR")
            delta =  pg.Point(np.clip(delta[0], -50, 50), np.clip(-delta[1], -50, 50))
            scale = 1.01 ** delta
            self.scale(scale[0], scale[1], center=self.mapToScene(self.mousePressPos))
            self.sigDeviceRangeChanged.emit(self, self.range)

        elif ev.buttons() in [QtCore.Qt.MidButton, QtCore.Qt.LeftButton]:  ## Allow panning by left or mid button.
            px = self.pixelSize()
            tr = -delta * px
            
            #self.translate(tr[0], tr[1])
            #self.sigDeviceRangeChanged.emit(self, self.range)
class InfiniteLineWithBreak(pg.GraphicsObject):

    def __init__(self, changeX, levelsY, pen=None):
        pg.GraphicsObject.__init__(self)

        self.changeX = changeX
        self.levelsY = levelsY

        self.maxRange = [None, None]
        self.moving = False
        self.movable = False
        self.mouseHovering = False

        pen = (200, 200, 100)
        self.setPen(pen)
        self.setHoverPen(color=(255,0,0), width=self.pen.width())
        self.currentPen = self.pen


    def setBounds(self, bounds):
        self.maxRange = bounds
        self.setValue(self.value())

    def setPen(self, *args, **kwargs):
        self.pen = pg.fn.mkPen(*args, **kwargs)
        if not self.mouseHovering:
            self.currentPen = self.pen
            self.update()

    def setHoverPen(self, *args, **kwargs):
        self.hoverPen = pg.fn.mkPen(*args, **kwargs)
        if self.mouseHovering:
            self.currentPen = self.hoverPen
            self.update()

    def boundingRect(self):
        br = self.viewRect()
        return br.normalized()

    def paint(self, p, *args):
        br = self.boundingRect()
        p.setPen(self.currentPen)
        # three lines (left border to change point, change point vertical, change point to right)
        p.drawLine(pg.Point(br.left(), self.levelsY[0]), pg.Point(self.changeX, self.levelsY[0]))
        p.drawLine(pg.Point(self.changeX, self.levelsY[0]), pg.Point(self.changeX, self.levelsY[1]))
        p.drawLine(pg.Point(self.changeX, self.levelsY[1]), pg.Point(br.right(), self.levelsY[1]))

    def dataBounds(self, axis, frac=1.0, orthoRange=None):
        if axis == 0:
            return None   ## x axis should never be auto-scaled
        else:
            return (0,0)

    def setMouseHover(self, hover):
        pass