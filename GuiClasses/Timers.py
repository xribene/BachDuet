from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
from ParsingClasses import RhythmTemplate
import time
import logging
from utils import Params

logger = logging.getLogger('default.'+__name__)
class Clock(QObject):
    clockSignal = pyqtSignal(dict)
    def __init__(self, appctxt):
        super(Clock, self).__init__()
        self.stopped = False
        
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.metronomeBPM =  self.config.default['metronome']["BPM"]
        self.old = time.time()
        self.setTimeSignature(self.config.timeSignature)
        #self.daemon = True 
        self.tick = 0
        self.globalTick = 0
        logger.warning("inside clock")
        self.paused = True  
    def changeBpm(self, value):
        self.metronomeBPM = value
    def setTimeSignature(self, timeSignature):
        [nom,denom] = timeSignature.split("/")
        nom = int(nom)
        denom = int(denom)
        self.timeSignature = timeSignature
        self.dur = nom*(16//denom)
        self.tick = 0
        # print(f"nom {nom} denom {denom} dur {self.dur}")
        self.RhythmTemplate = RhythmTemplate(self.timeSignature)
        self.rhythmTokens = self.RhythmTemplate.getRhythmTokens(self.dur,'last')
    def stopit(self):
        self.stopped=True
    def pauseResumeClock(self):
        self.paused = self.paused ^ True
        print(f"paused = {self.paused}")
    def reset(self):
        self.tick = 0
    @pyqtSlot()
    def run1(self):
        while not self.stopped:
            if not self.paused:
                time.sleep(60/self.metronomeBPM/4)
                # QThread.sleep(60/self.metronomeBPM/4)
                clockTriger = {
                    'tick' : self.tick,
                    'rhythmToken' : self.rhythmTokens[self.tick],
                    'metronomeBPM' : self.metronomeBPM,
                    'globalTick' : self.globalTick
                }
                    # [self.tick,self.rhythmTokens[self.tick], self.metronomeBPM]
                #print(f"\n\n\n Clock to emit {clockTriger} at time {time.time()}")
                self.clockSignal.emit(clockTriger)
                self.tick += 1 
                self.globalTick +=1
                if self.tick == self.dur:
                    self.tick = 0
            else:
                time.sleep(0.02) 
class TempoEstimator(QObject):
    updateTempoSignal = pyqtSignal(int)
    def __init__(self, params):
        super(TempoEstimator, self).__init__(None)
        self.params = params
        self.metronomeBPM =  self.params['metronome']["BPM"]
        self.queue = []
    @pyqtSlot(int)
    def changeBpm(self, value):
        self.metronomeBPM = value
    @pyqtSlot(float)
    def dur2bpm(self, duration):
        raise NotImplementedError


class Metronome(QObject):
    #metronomeSignal = pyqtSignal()
    metronome2managerSignal = pyqtSignal(dict)
    def __init__(self, appctxt, parentPlayer, parent):
        super(Metronome, self).__init__(None) # cant move objects with parent, to threads
        self.parentPlayer = parentPlayer
        self.parent = parent
        self.status = True
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.channel = self.parentPlayer.channelOut # 144 + params['metronome']["midiChanOut"] - 1
        self.volume = self.parentPlayer.volume #params['metronome']["volume"]
        self.beep2pitch =  self.parentPlayer.pitch2 # params['metronome']["pitch2"]
        self.beep1pitch =  self.parentPlayer.pitch1
        self.timeSignature2ticks(self.config.timeSignature)
        logger.warning('inside metronome')
    def timeSignature2ticks(self, timeSignature):
        [nom,denom] = timeSignature.split("/")
        nom = int(nom)
        denom = int(denom)
        self.timeSignature = timeSignature
        self.dur = nom*(16//denom)
    
    @pyqtSlot()
    def changeMetronomeStatus(self):
        self.status = self.status ^ True
    @pyqtSlot(dict)
    def process(self, clockTrigger):
        # triggarei synexeia, oxi mono otan prepei na akoustei. Otan den prepei na akoustei apla stelnei None sto pitch. To ekana gia na douleuei kalytera o Manager
        #print(f"In {self.__class__.__name__} "clockTriger)
        tick = clockTrigger['tick']
        rhythmToken = clockTrigger['rhythmToken']
        globalTick = clockTrigger['globalTick']
        output = {
            "playerName" : self.parentPlayer.name, 
            "keyEstimation" : None,
            "midi" : None,
            "artic": 0,
            "tick": tick,
            "globalTick" : globalTick,
            "rhythmToken": rhythmToken
        }
        if self.status and (tick)%4==0:
            # it enters here every 4 16th notes, or every quarter beat.
            # self.parent.toolbar.lcd.display(tick//4+1)
            #self.parent.toolbar.lcd.setDig
            # self.le = QLineEdit()
            # self.le.setText(str(tick)+"  ")
            # self.parent.toolbar.lcd.display(self.le.text())
            tempBeep = self.parentPlayer.pitch2
            if (tick+self.dur)%self.dur==0: # it enters here only in the first beat
                tempBeep = self.parentPlayer.pitch1
            #self.midiOut.send_message(self.beepOff)
            #print(f"Metronome to emit trigger {clockTrigger}")
            output['midi'] = tempBeep
            output['artic'] = tick
        #print(f"o metronomos esteile {output} at time {time.time()}")
        self.metronome2managerSignal.emit(output)
            #self.metronomeSignal.emit()
            
            #self.midiOut.send_message(self.beepOn)