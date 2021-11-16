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
    """ The clock of the app

    For this class I didn't use the slot mechanism of Qt. 
    The while loop that runs in the run1() method, blocks the
    event loop, and it can't accept signals from other modules. 

    Also, to create the clock signal, I used time.sleep() inside
    a while loop, instead of  using a QTimer (like I did for example
    in MidiKeyboardReaderAsync()), because I wanted the speed of the 
    clock to be adjustable by the user. 

    Attributes:
        stopit: when True, the clock stops
        config: the config file for the app
        metronomeBPM: the metronome BPM affects
            the speed of the clock
        dur: the number of 16th's in one measure.
            It depends on the timeSignature. 
        tick: counter of the clock "ticks".
            0 <= tick < dur
        globalTick: counts the total number of 
            ticks "played" in the current session
        rhythmTokens: a list of the rhythmTokens
            for the current timeSignature. 
            I.e for 4/4 and tick=0, token is 1_0_0
            (see the paper for details)
        paused: True when clock is paused

    Signals:
        clockSignal(dict): it emits on every "tick" (16th note)
            and it is connected with slots in most of the 
            other modules.

    Methods:
        changeBpm(value): This function works like a setter 
            for the metronomeBPM attribute. Normally it should
            be a slot().
        timeSign2dur(timeSignature) : finds the duration of 
            a measure in 16th notes, for the given timeSignature
        stopClock(): sets the stopit flag to True
        pauseResumeClock(): changes the paused flag to the 
            oposite value of that it had before. 
        reset(): resets the tick counter. It is called every
            time the user resets the memory of the neural net
        run1(): the function that generates the clock signal.
            It uses a while loop, with the time.sleep() function

    """
    clockSignal = pyqtSignal(dict)

    def __init__(self, appctxt):
        super(Clock, self).__init__()
        self.stopit = False
        
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.metronomeBPM =  self.config.default['metronome']["BPM"]
        self.setTimeSignature(self.config.timeSignature)
        self.tick = 0
        self.globalTick = 0
        self.paused = True  
    def changeBpm(self, value):
        self.metronomeBPM = value
    def setTimeSignature(self, timeSignature):
        [nom,denom] = timeSignature.split("/")
        nom = int(nom)
        denom = int(denom)
        self.dur = nom*(16//denom)
        self.tick = 0
        rhythmTemplate = RhythmTemplate(timeSignature)
        self.rhythmTokens = rhythmTemplate.getRhythmTokens(self.dur,'last')
    def stopClock(self):
        self.stopit=True
    def pauseResumeClock(self):
        self.paused = self.paused ^ True
        print(f"paused = {self.paused}")
    def reset(self):
        self.tick = 0
    @pyqtSlot()
    def run1(self):
        while not self.stopit:
            if not self.paused:
                time.sleep(60/self.metronomeBPM/4)
                clockTriger = {
                    'tick' : self.tick,
                    'rhythmToken' : self.rhythmTokens[self.tick],
                    'metronomeBPM' : self.metronomeBPM,
                    'globalTick' : self.globalTick
                }
                #print(f"\n\n\n Clock to emit {clockTriger} at time {time.time()}")
                self.clockSignal.emit(clockTriger)
                self.tick += 1 
                self.globalTick +=1
                if self.tick == self.dur:
                    self.tick = 0
            else:
                # used to reduce the CPU usage. If ommited, temperature
                # rises to max. 
                time.sleep(0.02)
    def singleRun(self):
        clockTriger = {
            'tick' : self.tick,
            'rhythmToken' : self.rhythmTokens[self.tick],
            'metronomeBPM' : self.metronomeBPM,
            'globalTick' : self.globalTick
        }
        self.tick += 1 
        self.globalTick +=1
        if self.tick == self.dur:
            self.tick = 0
        return clockTriger
 
class TempoEstimator(QObject):
    """Currently not used."""
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
    """ The metronome player/agent

    This class works in sync with the clock, and
    is responsible for sending "beep" sounds to 
    indicate each beat of the measure. I.e in a 
    4/4 time signature, the clock emits 16 signals 
    (ticks) per measure, the metronome receives all
    of them, and generates sound every 4 "ticks"

    Attributes:
        stopit: when True, the clock stops
        config: the config file for the app
        metronomeBPM: the metronome BPM affects
            the speed of the clock
        dur: the number of 16th's in one measure.
            It depends on the timeSignature. 
        tick: counter of the clock "ticks".
            0 <= tick < dur
        globalTick: counts the total number of 
            ticks "played" in the current session
        rhythmTokens: a list of the rhythmTokens
            for the current timeSignature. 
            I.e for 4/4 and tick=0, token is 1_0_0
            (see the paper for details)
        paused: True when clock is paused

    Signals:
        metronome2managerSignal(dict): it emits on every "tick" (16th note)
            and it is connected with slots in most of the 
            other modules.

    Methods:
        timeSign2dur(timeSignature) : finds the duration of 
            a measure in 16th notes, for the given timeSignature
        process(clockTrigger): A slot, that runs every time the clock
            emits its signal (every "tick"/16th). It gets the current
            "tick" from the clock, and it decides whether to send 
            a "beep" sound to the Manager(). The "beep" sound for the
            first beat of the measure (pitch1) is different from the 
            rest beats (pitch2)

    """

    metronome2managerSignal = pyqtSignal(dict)
    def __init__(self, appctxt, parentPlayer):
        super(Metronome, self).__init__(None) # cant move objects with parent, to threads
        self.parentPlayer = parentPlayer
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.timeSign2dur(self.config.timeSignature)

    def timeSign2dur(self, timeSignature):
        [nom,denom] = timeSignature.split("/")
        nom = int(nom)
        denom = int(denom)
        self.dur = nom*(16//denom)
    
    @pyqtSlot(dict)
    def process(self, clockTrigger):
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
        if (tick)%4==0:
            # it enters here every 4 16th notes, or every quarter beat.
            # TODO currently this works only when we have 4 beats in the measure
            # the extension to more timeSignature is straight forward
            tempBeep = self.parentPlayer.pitch2
            if (tick+self.dur)%self.dur==0: # it enters here only in the first beat
                tempBeep = self.parentPlayer.pitch1
            output['midi'] = tempBeep
            output['artic'] = tick
        # Metronome emits its signal, on every 16th note, and not on every beat
        # this is not intuitive, but it makes Manager() way easier to implement
        self.metronome2managerSignal.emit(output)