from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform)
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgWidget

from GuiClasses.StaffItem import *
from GuiClasses.Flag import *
#from GraphicsItems.NoteItem import *
import pickle
import numpy as np
from pathlib import Path

class StaffPainter(QObject):
    sendNoteItemToMain = pyqtSignal(list, int)

    def __init__(self, staffView, notesDict, appctxt ):
        super().__init__()
        self.staffView = staffView
        self.appctxt = appctxt
        self.svgFolder = Path("Images","svg")
        self.notesPainterDict = notesDict
        self.lineDistance = self.staffView.staffLines.lineDistance
        self.notePositions = self.staffView.staffLines.horNotePositions
        self.linePosStaff1 = self.staffView.staffLines.sopranoStaffLinePos
        self.linePosStaff2 = self.staffView.staffLines.bassoStaffLinePos
        self.totalLines = self.staffView.staffLines.totalLines
        
        #self.currentNotePosIndex = self.notePositions[0]
        self.sceneRect = self.staffView.mapToScene(self.staffView.viewport().geometry()).boundingRect()
        self.width = self.sceneRect.width()
        self.lastKeyboardStaffNoteObj = None
        self.lastHorizontalPos = self.notePositions[0] + self.lineDistance/2
        self.rightMostPointDnn = self.notePositions[0]+ self.lineDistance/2
        self.lastNoteHorPos = self.notePositions[0] + self.lineDistance/2
        self.lastNoteHorPosDnn = self.notePositions[0] + self.lineDistance/2
        self.rightMostPointKeyboard = self.notePositions[0] + self.lineDistance/2
        self.possibleDurations = [1,2,3,4,6,8,12,16,24]
        self.lastNote = None
        self.lastDur = 1
        self.lastNoteDnn = None
        self.lastDurDnn = 1
        self.lastKeyString = None
        self.lastDotItem = None
        self.aNoteWasPainted = False
        self.doubleBarLine = 0
        self.addClefs()
    
    @pyqtSlot()
    def resetEvent(self):
        # a slot that is activated when the user resets the neural nets memory
        # (random re-initialization of hidden states). In this case we want to 
        # display a doubleBarLine
        self.doubleBarLine = 1
    @pyqtSlot(float)
    def viewChanged(self, zoomFactor):
        print("zoom changed")
        self.sceneRect = self.staffView.mapToScene(self.staffView.viewport().geometry()).boundingRect()
        self.width = self.sceneRect.width()# / zoomFactor
        #pass
        #self.sceneRect = self.staffView.mapToScene(self.staffView.viewport().geometry()).boundingRect()
        #self.lineDistance = self.lineDistance / zoomFactor #self.sceneRect.height() / (self.totalLines + 1)
    def addClefs(self):
        # i will not use the signal to main here, but I ll directly
        # use self.staffView.staffScene.addItem(....)
        # because this runs in the init, and the event loops have not started yet
        self.svgTreble = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/clefTreble.svg'))#, parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgTreble)
        height = self.svgTreble.boundingRect().height()
        width = self.svgTreble.boundingRect().width()
        self.svgTreble.scale(3*self.lineDistance/width, 10*self.lineDistance/height)
        self.svgTreble.setPos(0, self.linePosStaff1[0]-3.5*self.lineDistance)

        self.svgBass = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/clefBass.svg'))#,parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgBass)
        height = self.svgBass.boundingRect().height()
        width = self.svgBass.boundingRect().width()
        self.svgBass.scale(3*self.lineDistance/width, 4*self.lineDistance/height)
        self.svgBass.setPos(0, self.linePosStaff2[0])

        self.svgNom = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/timeSign4.svg'))#, parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgNom)
        height = self.svgNom.boundingRect().height()
        width = self.svgNom.boundingRect().width()
        self.svgNom.scale(2*self.lineDistance/width, 2*self.lineDistance/height)
        self.svgNom.setPos(3.5*self.lineDistance, self.linePosStaff1[0])

        self.svgDeNom = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/timeSign4.svg'))#, parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgDeNom)
        height = self.svgDeNom.boundingRect().height()
        width = self.svgDeNom.boundingRect().width()
        self.svgDeNom.scale(2*self.lineDistance/width, 2*self.lineDistance/height)
        self.svgDeNom.setPos(3.5*self.lineDistance, self.linePosStaff1[2])

        self.svgNom = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/timeSign4.svg'))#, parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgNom)
        height = self.svgNom.boundingRect().height()
        width = self.svgNom.boundingRect().width()
        self.svgNom.scale(2*self.lineDistance/width, 2*self.lineDistance/height)
        self.svgNom.setPos(3.5*self.lineDistance, self.linePosStaff2[0])

        self.svgDeNom = QtSvg.QGraphicsSvgItem(self.appctxt.get_resource('Images/svg/timeSign4.svg'))#, parent = self.staffView.staffLines)
        self.staffView.staffScene.addItem(self.svgDeNom)
        height = self.svgDeNom.boundingRect().height()
        width = self.svgDeNom.boundingRect().width()
        self.svgDeNom.scale(2*self.lineDistance/width, 2*self.lineDistance/height)
        self.svgDeNom.setPos(3.5*self.lineDistance, self.linePosStaff2[2])
    #def addTimeSignature(self):
    
    # # @pyqtSlot(list, int)
    # def updateStaffView(self, items, mode):
    #     #print(f"receivedSvgItem {items[0].__class__}")
    #     for item in items:
    #         if mode == 1:
    #             self.staffView.staffScene.addItem(item)
    #         elif mode == 0:
    #             self.staffView.staffScene.removeItem(item)
   
    @pyqtSlot(list)
    def getNewNoteEvent(self, currentNotes):
        
        correctionDnn = 0
        correctionKeyboard = 0
        newNote = 1
        [newNoteDnn, newNoteKeyboard, newMetronomeBeep] = currentNotes
        keyString = newNoteDnn['keyEstimation']
        # try:
        #     [newNoteDnn, newNoteKeyboard, newMetronomeBeep] = self.currentNotesForPainter.get(block=False)
        #     keyString = newNoteDnn['keyEstimation']
        #     #print(f"received {[newMetronomeBeep]}")
        #     newNote = 1
        #     #print(f"metronome {newMetronomeBeep}\ndnn {newNoteDnn}\nkeyboard {newNoteKeyboard}")
        #     #check for each of them
        #     #first newNoteDnn [midi, hit, tick]
        # except BaseException as e:
        #     #print(e)
        #     newNote = 0
        #     #print(f"EROOR {e} sto tick")
        #     #sceneRect3 = self.staffView.viewport()
        #     #sceneRect4 = self.staffView.viewPort().geometry()
        #     pass
        if newNote == 1: # if newToken , it can be new note, it can be rest, or continuation, its 1 at every 16th note.
            if newNoteKeyboard['midi'] == 0 and self.lastNote == 0: # if midiNumber == 0 , so REST, and self.lastNote was also a rest
                newNoteKeyboard['artic'] = 0 # tote kane to articulation 0 . just a heuristic giati genika kanw plot otan erthei to epomeno articulation=1
                # an den to ekana auto tote that ekana plot apeires 16th pauses
            tieToPrevKeyboard = 0
            ############ IF ONSET (OR MEASURE ENDING), THEN PLOT THE PREVIOUS Note
            if newNoteKeyboard['artic'] == 1 or newMetronomeBeep['tick'] == 0:
                if self.lastNote is not None: # POTE EINAI NONE ? MONO STHN POLI ARXI
                    # THELOUME NA KANOUME PLOT TIN PROHGOUMENH MONO OTAN YPHRXE PROHGOUMENI NOTA
                    # finalize and send prevDnnStaffSymbol for plotting
                    midiNumber = self.lastNote
                    staffInd = 0
                    barLine = 0
                    dur = self.lastDur
                    # find if we want primary or secondary
                    #print(f"for midinumber {midiNumber}, keyQuery {keyString}, keysInPrimary {self.notesPainterDict[midiNumber]['primary']['keys']}")
                    
                    if (keyString is not None) and (keyString != 'None'):
                        primOrSec = 'primary' if keyString in self.notesPainterDict[midiNumber]['primary']['keys'] else 'secondary'
                    else:
                        primOrSec = 'primary' 
                    noteAddProps = self.notesPainterDict[midiNumber][primOrSec] 
                    if newMetronomeBeep['tick'] == 0: # if tick == 0 , new bar
                        barLine = 1
                        tieToPrevKeyboard = 0
                    self.rightMostPointKeyboard = self.prepareSymbolObjForPaint(midiNumber = midiNumber, horPos = self.lastHorizontalPos - dur*3*self.lineDistance, staffInd = staffInd, 
                                                    dur = dur, props = noteAddProps, barLine = barLine, clef = 'treble', tieToPrev = tieToPrevKeyboard)
                    aaa = self.rightMostPointKeyboard - (self.lastHorizontalPos - dur*3*self.lineDistance + 1.8*self.lineDistance)
                    self.lastNoteHorPos = self.lastHorizontalPos - dur*3*self.lineDistance
                    # correctionKeyboard = max([aaa, 0])
                    if aaa < 1/20:
                        correctionKeyboard = 0 
                    self.aNoteWasPainted = True
                    #print(f"rightMostPoint {self.rightMostPointKeyboard}")
                    #self.finalizeLastSymbol()
                    # create the new Symbol
                    #self.lastKeyboardStaffNoteObj = StaffSymbol(midiNumber=newNoteDnn['midi'])
                self.lastDur = 1
                self.lastNote = newNoteKeyboard['midi']
                #self.lastHorizontalPos += 3*self.lineDistance
            elif newNoteKeyboard['artic'] == 0:
                if newMetronomeBeep['tick'] != 0:
                    #print(f" newNoteDnn['artic'] {newNoteKeyboard['midi']} == self.lastNote {self.lastNote}")
                    if newNoteKeyboard['midi'] == self.lastNote: #TODO IF NOT ??? gamise ta tote 
                        # update lastDnnStaffSymbol by increasing the duration
                        #self.lastKeyboardStaffNoteObj.duration += 1
                        self.lastDur += 1
            

            if keyString != self.lastKeyString : 
                #print(keyString)
                # keyItem = QtSvg.QGraphicsSvgItem('<svg height="30" width="200"><text x="0" y="15" fill="red">Amajor</text></svg>')
                #print(keyString)
                # filePath = self.appctxt.get_resource(str("Cmajor.svg"))
                # keyItem = QtSvg.QGraphicsSvgItem(filePath)
                # keyItem.setPos(self.lastHorizontalPos, 10)
                # keyItem.scale(0.5,0.5)
                #keyItem.setGeometry(self.lastHorizontalPos, 20, 20,20)
                realKeyString = keyString.split(" ")[0]+'m' if 'minor' in keyString else keyString.split(" ")[0]
                print(realKeyString)
                svg_str = f"""
                <svg height="20" width="20">
                <text x="0" y="10" style="font-style:normal;font-weight:bold;letter-spacing:0px;word-spacing:0px;fill:#4a85c4;fill-opacity:1;stroke:none;stroke-width:0.26458332">{realKeyString}</text>
                </svg>
                """
                svg_bytes = bytearray(svg_str, encoding='utf-8')
                svgItem = QtSvg.QGraphicsSvgItem()
                renderer = QtSvg.QSvgRenderer()
                renderer.load(svg_bytes)
                svgItem.setSharedRenderer(renderer)
                svgItem.setPos(self.lastHorizontalPos, 5)
                svgItem.scale(2,2)
                self.sendNoteItemToMain.emit([svgItem],1) # TODO
                # # self.updateStaffView([svgItem],1)
                # for item in [svgItem]:
                #     self.staffView.staffScene.addItem(item)
                    
                self.lastKeyString = keyString
            #print(f"{newMetronomeBeep} {newMetronomeBeep['tick'].__class__}")
            if newMetronomeBeep['tick']%4==0 :
                # THE DOTS THAT DUAN ASKED GAMW THN PANAGIA
                filePath = self.appctxt.get_resource(str(self.svgFolder/"pointer.svg"))
                dotItem = QtSvg.QGraphicsSvgItem(filePath)
                dotItem.setPos(self.lastHorizontalPos, 10)
                # heightBefore = self.boundingRect().height()
                # widthBefore = self.boundingRect().width()
                # widthScale = self.widthRel * self.lineDistance / self.widthBefore
                # heightScale = self.heightRel * self.lineDistance / self.heightBefore
                dotItem.scale(0.25,0.25)
                if self.lastDotItem is not None:
                    # self.staffView.staffScene.removeItem(self.lastDotItem)
                    self.sendNoteItemToMain.emit([self.lastDotItem],0)
                    # self.updateStaffView([self.lastDotItem],0)
                self.sendNoteItemToMain.emit([dotItem],1)
                # self.staffView.staffScene.addItem(dotItem)
                # self.updateStaffView([dotItem],1)
                self.lastDotItem = dotItem
            
            ##########################################################################################################################
            #######################    SAME FOR DNN ###################################################################################
            if newNoteDnn['midi'] == 0 and self.lastNoteDnn == 0:
                newNoteDnn['artic'] = 0
            if newNoteDnn['artic'] == 1 or newMetronomeBeep['tick'] == 0:
                tieToPrevDnn = 0
                if self.lastNoteDnn is not None:
                    # finalize and send prevDnnStaffSymbol for plotting
                    midiNumber = self.lastNoteDnn
                    staffInd = 1
                    barLine = 0
                    dur = self.lastDurDnn
                    
                    #print(f"for midinumber {midiNumber}, keyQuery {keyString}, keysInPrimary {self.notesPainterDict[midiNumber]['primary']['keys']}")
                    if (keyString is not None) and (keyString != 'None'):
                        primOrSec = 'primary' if keyString in self.notesPainterDict[midiNumber]['primary']['keys'] else 'secondary'
                    else:
                        primOrSec = 'primary'
                    noteAddProps = self.notesPainterDict[midiNumber][primOrSec]
                    #noteAddProps = self.notesPainterDict[midiNumber]['primary'] # for now, use only the primary version of the note (ie C instead of B#)
                    if newMetronomeBeep['midi'] == 70:
                        tieToPrevDnn = 0
                    #print(midiNumber)
                    self.rightMostPointDnn = self.prepareSymbolObjForPaint(midiNumber = midiNumber, horPos = self.lastHorizontalPos - dur*3*self.lineDistance, 
                                                    
                                                    staffInd = staffInd, dur = dur, props = noteAddProps, barLine = barLine, clef = 'bass', tieToPrev = tieToPrevDnn)
                    self.lastNoteHorPosDnn = self.lastHorizontalPos - dur*3*self.lineDistance
                    self.aNoteWasPainted = True
                    bbb = self.rightMostPointDnn - (self.lastHorizontalPos - dur*3*self.lineDistance + 1.8*self.lineDistance)
                    #correctionDnn = max([bbb, 0])
                    if correctionDnn < 1/20:
                        correctionDnn = 0 
                    #self.finalizeLastSymbol()
                    # create the new Symbol
                    #self.lastKeyboardStaffNoteObj = StaffSymbol(midiNumber=newNoteDnn['midi'])
                self.lastDurDnn = 1
                self.lastNoteDnn = newNoteDnn['midi']
                #self.lastHorizontalPos += 3*self.lineDistance
            elif newNoteDnn['artic'] == 0:
                # rightMostPointDnn += 3*self.lineDistance
                if newMetronomeBeep['tick'] != 0:
                    #print(f" newNoteDnn['artic'] {newNoteKeyboard['midi']} == self.lastNote {self.lastNote}")
                    if newNoteDnn['midi'] == self.lastNoteDnn:
                        # update lastDnnStaffSymbol by increasing the duration
                        #self.lastKeyboardStaffNoteObj.duration += 1
                        self.lastDurDnn += 1
                        #print(f"  {self.lastDur}")
            # print(f"lastHorPos {self.lastHorizontalPos}, corKeyboard {correctionDnn} , corDnn {correctionDnn}")
            # print(f"max is { max([correctionDnn, correctionKeyboard])}")
            self.lastHorizontalPos += max([correctionDnn, correctionKeyboard])
            # print(f"lastHorPosAfterMax {self.lastHorizontalPos}\n\n\n\n\n")
            self.lastHorizontalPos += 3*self.lineDistance
            # print(f"lastHorPosAfter {self.lastHorizontalPos}\n\n\n\n\n")
            # if self.aNoteWasPainted is True:
            #     print(f"max of lastHorPos {self.lastHorizontalPos} , rightMost+d {self.rightMostPointKeyboard + self.lineDistance} , rightMostDnn+d {self.rightMostPointDnn +self.lineDistance }")
            #     self.lastHorizontalPos = max([self.lastHorizontalPos, self.rightMostPointKeyboard + self.lineDistance, self.rightMostPointDnn + self.lineDistance]) 
            #     self.aNoteWasPainted = False
            #print(f"lastHorPos {self.lastHorizontalPos}")
            #sceneRect2 = self.staffView.viewport().geometry().boundingRect()
            #print(f"sceneRect inside painter {sceneRect.width()} and pos is {self.currentNotePosIndex}")
            ###################self.currentNotePosIndex = max([rightMostPointKeyboard, rightMostPointDnn]) + self.lineDistance
            #sceneRect1 = self.staffView.mapToScene(self.staffView.viewport().geometry()).boundingRect()
            #sceneRect2 = self.staffView.mapToGlobal(self.staffView.viewport().geometry()).boundingRect()
            #sceneRect3 = self.staffView.viewport()
            #sceneRect4 = self.staffView.viewPort().geometry()
            #print(self.sceneRect.x() + self.sceneRect.width())
            #print(self.currentNotePosIndex)
            #print(f"geom2Scene {sceneRect1}")#", \ngeom2Global{sceneRect3}")#", \ngeom {sceneRect4}\n\n\n")
            
            if self.lastHorizontalPos > self.width:
                # print(self.lastHorizontalPos)
                #self.staffView.horizontalScrollBar().setValue(self.staffView.horizontalScrollBar().value() +  dur* 3*self.lineDistance)
                #print(self.width)
                self.staffView.horizontalScrollBar().setValue(self.lastHorizontalPos - self.width/1)
                #sceneRect2 = self.staffView.mapToScene(self.staffView.viewport().geometry()).boundingRect()
                #self.svgTreble.setPos(sceneRect2.x(), self.linePosStaff1[0]-3.5*self.lineDistance)
        
        # except BaseException as e:
        #     traceback.print_exc()
        # 
    def prepareSymbolObjForPaint(self, midiNumber ,horPos, staffInd , dur , props, barLine, clef, tieToPrev):
        #print(f" MPAINW MESA ME HOR POS {horPos}")
        rightMostPoint = 0
        initHorPos = horPos
        addBarLine = 0
        if staffInd == 0:
            vertPosLookUp = self.linePosStaff1
        elif staffInd == 1:
            vertPosLookUp = self.linePosStaff2
        if midiNumber is not None: # is not None
            # first check the duration, and decide if it should be splitted to two svg notes and how ( like calculating coins for change)
            aaa = []
            durSplitted = self.durationSplitter(dur,aaa)
            noteSymbolsCount = len(durSplitted)
            #print(durSplitted)
            
            for i in range(noteSymbolsCount):
                lastNoteHorPos = self.lastNoteHorPos if staffInd == 0 else self.lastNoteHorPosDnn
                if i == 0 :
                    horPos = initHorPos
                    
                    #print(f"initPos {horPos} the next one should be at {horPos+3*self.lineDistance*durSplitted[i]} since dur is {durSplitted[i]}")
                else :
                    #horPos = initHorPos + 3*self.lineDistance * durSplitted[i-1]
                    horPos = rightMostPoint + self.lineDistance + 3*self.lineDistance * (durSplitted[i-1] -1 )
                    tieToPrev = 1
                if i == noteSymbolsCount - 1 and barLine == 1:
                    addBarLine = 1
                    
                    #print(f"pos for i={i} is {horPos} the next one should be at {horPos+3*self.lineDistance*durSplitted[i]}")
                # edw tha apofasisw gia position katheto. Gia orizontal apofasise o getNewNoteEvent. Gia dimension tha apofasisei o getTheRightSvgFile.
                # episis tha apofasisw gia extraLine kai gia accidental
                tempDur = durSplitted[i]
                #print(f"{props['treble']['pos']} {props['acc']}")
                # EDW FTIAXNW TO VERT POS
                
                vertPosRel = float(props[clef]['pos'])
                
                vertPos = vertPosLookUp[0] + vertPosRel * self.lineDistance
                # υπολογισε extra lines edw me vasi to vertPosRel
                extraLinesAbove = int(np.ceil(np.abs(vertPosRel))-1 if vertPosRel < -1 else 0)
                extraLinesBellow = int(np.ceil(vertPosRel)-4 if vertPosRel > 4 else 0)
                # if props[clef]['extraLine'] is None:
                #     extraLine = 0
                # else:
                #     extraLine = float(props[clef]['extraLine'])
                if props['acc'] is None:
                    acc = 0
                else:
                    acc = float(props['acc'])
                # bring me note svg
                if self.doubleBarLine == 1:
                        addBarLine = 2
                items, rightMostPoint = self.bringMeTheSvg(midiNumber = midiNumber, dur = tempDur, vertPos = vertPos, 
                                                    horPos = horPos, lastNoteHorPos = lastNoteHorPos, acc = acc, tieToPrev = tieToPrev, vertPosLookUp = vertPosLookUp,
                                                    extraLines = [extraLinesAbove, extraLinesBellow], addBarLine = addBarLine)
                if self.doubleBarLine == 1:
                        self.doubleBarLine = 0
                if staffInd ==0 :
                    self.lastNoteHorPos = horPos
                else:
                    self.lastNoteHorPosDnn = horPos
                #lastNoteHorPos = self.lastNoteHorPos if staffInd == 0 else self.lastNoteHorPosDnn
                if i >0:
                    if staffInd == 0:
                        self.lastNoteHorPos = horPos
                    else:
                        self.lastNoteHorPosDnn = horPos
                # print(f"dur = {dur}, i = {i}, total = {noteSymbolsCount}, barLine {addBarLine}, horPos {horPos}, rightMost {rightMostPoint}")
                self.sendNoteItemToMain.emit(items, 1)
                # return None
                # self.updateStaffView(items,1)
        return rightMostPoint
               
                


    def bringMeTheSvg(self, midiNumber, dur, vertPos, horPos, lastNoteHorPos, acc, tieToPrev, vertPosLookUp, extraLines, addBarLine):
        svgFolder = self.svgFolder
        svgItems = []
        note = Note(midiNumber = midiNumber, dur = dur, acc = acc, tieToPrev = tieToPrev, vertPosLookUp = vertPosLookUp, extraLines = extraLines,
                        svgFolder = svgFolder, lineDistance = self.lineDistance, invert = False, horPos = horPos, lastNoteHorPos = lastNoteHorPos,
                         vertPos = vertPos, addBarLine = addBarLine, appctxt = self.appctxt)
        #print(svgItem.__class__)
        svgItems.append(note)
        #print(note.rightMostPoint)
        return svgItems, note.rightMostPoint

    def durationSplitter(self, duration, splits = []):
        # find closest duration 
        closestDur = min([duration - i for i in self.possibleDurations if duration-i >=0])
        splits.append(duration-closestDur)
        if closestDur == 0:
            return splits
        else:
            return self.durationSplitter(closestDur,splits)