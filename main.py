""" 
Main script for BachDuet Application
           
Usage
-----
python main.py

"""

# fbs import
#from fbs_runtime.application_context import ApplicationContext
# pyQt5 imports
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, QDateTimeEdit,QMessageBox,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit, QSplashScreen,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox,QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsObject, QGraphicsLineItem,
                         QGraphicsScene, QGraphicsView, QStyle, QWidget, QLabel, QHBoxLayout, QMenuBar, QTextEdit, QGridLayout, QAction, QActionGroup, QToolBar, QToolBox, QToolButton)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread, QPointF, QRectF, QLineF, QRect
from PyQt5.QtGui import (QPen, QTransform, QPixmap)
from PyQt5.QtSvg import QGraphicsSvgItem
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# python imports
import logging
import logging.config
from collections import deque,  OrderedDict
from queue import Queue
import time, threading
import sys
import argparse
import random
import rtmidi
from datetime import datetime
from functools import partial
import numpy as np
from pathlib import Path
import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import weight_norm
import torch.optim as optim 
#from Models.LSTMCell import LSTM as LSTM_Duet
import sys
# custom imports
from GuiClasses.MidiKeyboard import MidiKeyboardReaderAsync, MidiReaderSync
from GuiClasses.Timers import Clock, Metronome, TempoEstimator
from GuiClasses.NeuralNetworkIsmir import NeuralNetSync, NeuralNet
from GuiClasses.AudioRecording import YinEstimator, Audio2MidiEvents, AudioRecorder
from GuiClasses.StaffItem import Staff
from GuiClasses.StaffPainter import StaffPainter
from GuiClasses.StaffView import StaffView
from GuiClasses.Mixer import *
from GuiClasses.Manager import *
from GuiClasses.MenuBar import *
from GuiClasses.ToolBar import *
from GuiClasses.ModeWindow import *
from GuiClasses.Preferences import *
from GuiClasses.Player import *
from GuiClasses.PianoRollView import PianoRollView
from GuiClasses.PianoRollPainter import PianoRollPainter

from GuiClasses.Memory import Memory
from GuiClasses.InputDialog import InputDialog
from keyMapping import ddd as KeyMappings

from ParsingClasses import RhythmTemplate
from utils import Params, TensorBuffer, rename
from ParsingClasses import Vocabulary


class ApplicationContext(object):
    """
    Manages the resources. There is not
    actual need for this Class. The only reason
    to use it is for compatibility with the fbs
    library, in order to create an exe file for the app

    Methods
    -------
    get_resource(name) : str
        returns the path of a resource by name
    """
    def __init__(self):
        self.path = Path.cwd() / 'resources' / 'base'
    def get_resource(self, name):
        return str(self.path / name)

class BachDuet(QWidget):
    """
    The main module of BachDuet

    It is responsible for setting up the GUI windows, and initialize 
    all the submodules/threads of the system. 

    Attributes
    ----------
    appctxt : ApplicationContext()
        an ApplicationContext class that contains the path
        of the resources
    logger : Logger()
        the logger of the app
    parent : None
        BachDuet is the top in hierarchy QWidget, so it has 
        no parrent

    Methods
    -------
    showSplashScreen() : None
        creates a QSplashScreen object and displays the splash image, 
        for 1 second
    showModeWindow() : None
        show the mode window so the user can select between 
        HH, HM, MM modes
    setupBachDuet(buttonInd) : None
        setups the current BachDuet configuration, according to
        the button that the user selected in ModeWindow(). 
    getSubjectId(name): str
        it returns the unique ID of a user. If the user is new
        it assigns a new ID and it returns it.
    initUi() : None
        creates the basic windows of the app including 
        pianoroll, staffs, mixer, preferences box, toolbars etc
    createPianoRollGroup() : None
        creates the piano roll window
    createStaffGroup() : None
        creates the staff window
    createMiscGroup() : None
        currently not in used.
    setupThreads() : None
        initiates all the threads for every player
    signalsNslots() : None
        sets up the connections between the modules/threads.
        certain actions in one thread, trigger signals, which connect 
        to slot functions in another thread.
    setupDelayedThreadsAndSignals() : None
        some threads/connections "A" have to wait until some
        other threads "B" start. This method is a slot, which is activated
        after all the "B" threads have been set up
    changeAttribute(state, extra, player, attribute) : None
        manages all the changes in a players preferences.
        It is a slot that is connected to all the signals of the
        preference box fields. It requires the players name, the
        attribute name, and the new state of the attribute.
    updatePortsDict() : None
        scans for current midi devices, and updates the 
        midi ports list in preferences 
    openDefaultPorts() : None
        opens the default midi ports for each player
    connectToNewMidiInput(portInd, player) : None
        connects the midi input with id portInd
        to the player
    connectToNewMidiOutput(portInd, player) : None
        connects the midi output with id portInd
        to the player
    
    """
    ctrlSignal = pyqtSignal(str)
    def __init__(self, appctxt, logger, parent = None):
        super(BachDuet, self).__init__()
        logger.warning("message warning from BachDUet")
        self.setObjectName("BachDuet")
        # self.config contains system settings loaded from 
        # a json file using the Params() class from utils.py
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.cwd = Path.cwd()
        self.storagePath = self.cwd / self.config.storagePath
        self.appctxt = appctxt
        self.ctrlPressed = False
        
        # notesPainterDict is used for displaying the notes on the Staves,
        # and it contains all the information about each notes position in the Staff
        # as well as their spellin given different key configurations.
        with open(self.appctxt.get_resource('notesPainterDict.pickle'), 'rb') as handle:
            self.notesDict = pickle.load(handle)
        # initiates the event loop. event filter is an object that receives all 
        # events that are sent to this object. This function is inherited
        # from QWidget class
        self.installEventFilter(self)
        # set the QIcon of the App
        self.setWindowIcon(QtGui.QIcon(self.appctxt.get_resource('Images/bachDuetIconYellow1024.png')))
        # display the splashScreen
        self.showSplashScreen()

        self.showModeWindow()

    def showSplashScreen(self):
        # load the splash screen image
        splash_pix = QPixmap(self.appctxt.get_resource('Images/bachDuetSplashYellow1024.png'))
        splash_pix = splash_pix.scaled(400,400)
        # QSplashScreen is the actual splash screen object/window
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        # Sets the background as transparent (I think)
        self.splash.setMask(splash_pix.mask())
        # show the window for 1 second.
        # TODO find a better way instead of time.sleep, so the 
        # rest of the processes are not bloked. 
        self.splash.show()
        time.sleep(1)

    def showModeWindow(self):
        # ModeWindow contains 3 buttons (HH,HM,MM)
        self.modeWindow = ModeWindow(self.appctxt)
        self.modeWindow.show()
        # splash screen closes at the same time ModeWindow appears
        self.splash.finish(self.modeWindow)
        # Selecting one of the 3 buttons of modeWindow, triggers
        # a signal that activates setupBachDuet() function. 
        self.modeWindow.buttonGroup.buttonClicked[int].connect(self.setupBachDuet)
    
    @pyqtSlot(int)
    def setupBachDuet(self, buttonInd):
        #TODO find a way to remove the if blocks
        self.modeWindow.hide()
        # current time is used to time annotate the saved data
        now = datetime.now()
        # if user selected Human vs Machine (HM) in ModeWindow()
        if buttonInd == 0:
            # dialog box for the user(s) to input their names
            dialog = InputDialog(humanPlayers=1)
            if dialog.exec():
                fields = dialog.getInputs()
            # get the unique ID of the user. 
            humanId = self.getSubjectId(name = fields['fullName 1'])
            # every user has a folder where all his interactions are saved
            self.subjectPath = self.storagePath / f'{humanId}_{fields["fullName 1"]}'
            self.experimentPath = self.subjectPath / now.strftime("%d_%m_%Y_%H_%M_%S")
            self.experimentPath.mkdir(parents=True, exist_ok=True)

            #TODO in the future, every user will have their own personalized settings
            # currently for all users I use the default profile
            self.params = self.config.default
            # for the (HM) task we need a human a machine and a metronome player
            self.player1 = Player( name = fields['fullName 1'], type = 'human', params = self.params, realTimeInput = True, inputType = 'midi', modules = {}, holdFlag = False)
            self.player2 = Player( type = 'machine', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.player3 = Player( type = 'metronome', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.players = [self.player1, self.player2, self.player3]
            self.sessionName = 'Human Vs Machine'
            # initial BPM is loaded from the params.
            self.initBPM = self.params['metronome']["BPM"]  
                
        # if user selected Machine vs Machine (MM) in ModeWindow()
        elif buttonInd == 1:
            # similar comments with the buttonInd == 0
            self.params = self.config.default
            self.player1 = Player( type = 'machine', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.player2 = Player( type = 'machine2', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.player3 = Player( type = 'metronome', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.players = [self.player1, self.player2, self.player3]
            self.initBPM = self.params['metronome']["BPM"]
            self.sessionName = 'Machine Vs Machine'
            
        # if user selected Human vs Human (HH) in ModeWindow()  
        elif buttonInd == 2:
            # similar comments with the buttonInd == 0
            dialog = InputDialog(humanPlayers = 2)
            if dialog.exec():
                fields = dialog.getInputs()
            humanId1 = self.getSubjectId(name = fields['fullName 1'])
            humanId2 = self.getSubjectId(name = fields['fullName 2'])
            self.subjectPath = [self.storagePath / f'{humanId1}_{fields["fullName 1"]}', self.storagePath / f'{humanId2}_{fields["fullName 2"]}']
            self.experimentPath = [self.subjectPath[0] / now.strftime("%d_%m_%Y_%H_%M_%S"), self.subjectPath[1] / now.strftime("%d_%m_%Y_%H_%M_%S")]
            self.experimentPath[0].mkdir(parents=True, exist_ok=True)
            self.experimentPath[1].mkdir(parents=True, exist_ok=True)
            #TODO currently I use the folder of the first player to save the
            # generated data. Change it to save them in both folders.
            self.experimentPath = self.subjectPath[0] / now.strftime("%d_%m_%Y_%H_%M_%S")
            #TODO also here, each player should have its own parameters. 
            # Currently all human players use the default profile
            self.params = self.config.default
            self.player1 = Player( type = 'human', params = self.params, realTimeInput = True, inputType = 'midi', modules = {}, holdFlag = False)
            self.player2 = Player( type = 'human2', params = self.params, realTimeInput = True, inputType = 'midi', modules = {}, holdFlag = False)
            self.player3 = Player( type = 'metronome', params = self.params, realTimeInput = False, inputType = None, modules = {}, holdFlag = None)
            self.players = [self.player1, self.player2, self.player3]
            self.sessionName = 'Human Vs Human'
            self.initBPM = self.params['metronome']["BPM"]
        # for each player open a new midi output port.
        # only human player class has midi input.
        for player in self.players : 
            player.midiOut = rtmidi.MidiOut()
            if 'human' in player.type : 
                player.midiIn = rtmidi.MidiIn()
        
        # initialize the main UI
        self.initUi()
        # initialize all threads
        self.setupThreads()
        # define signals slots namely the communication rules
        # between threads.
        self.signalsNslots()
        # detect available midi input and output devices
        self.updatePortsDict()
        # open the default midi input and output devices
        # for each user
        self.openDefaultPorts()
        # after everything is set up,
        # show the BachDuet QWidget maximized.
        self.showMaximized()

    def getSubjectId(self, name):
        # subjects.txt contains all users and their unique ID
        subjectsFilePath = self.storagePath / 'subjects.txt' 
        self.storagePath.mkdir(parents=True, exist_ok=True)
        if Path(subjectsFilePath).exists() == True:
            readMode = 'r+'
        else: 
            readMode = 'w'
        found = False 
        i=-1       
        with open(subjectsFilePath, readMode) as f:
            if readMode == 'r+':
                lines = f.readlines()
                for i, line in enumerate(lines) : 
                    if name in line:
                        found = True
                        subjectId = int(line.strip().split(' - ')[0])
            # if new user, add them in subjects.txt and assign a new ID
            if not found : 
                subjectId = i+2
                f.write(f'{subjectId} - {name}\n')
        return subjectId
    
    def initUi(self):
        self.setWindowTitle('BachDuet')
        s = QStyleFactory.create('Fusion')
        self.setStyle(s)
        self.createPianoRollGroup()
        self.createStaffGroup()
        # self.createMiscGroup()
        self.mixer = Mixer(self.players, self.params, self.appctxt,self) # TODO 
        self.preferences = Preferences(self.players, self.params,self.appctxt,self) # TODO
        self.menuBar = MenuBar(self)
        self.toolbar = ToolBar(appctxt = self.appctxt, parent = self, params = self.params)
        mainLayout = QGridLayout(self) 
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.toolbar, 0,0,3,1, Qt.AlignLeft|Qt.AlignTop)
        mainLayout.addWidget(self.staffGroup, 1,0,6,1)
        mainLayout.addWidget(self.pianoRollGroup, 7,0,15,1)
        #mainLayout.addWidget(self.othersGroup, 3,0,1,1)
        self.setLayout(mainLayout)
    def createMiscGroup(self): 
        # NOTUSED
        self.othersGroup = QGroupBox("Other")
        self.timeSignatureComboBox = QComboBox(self)
        self.timeSignatureComboBox.addItems(['2/4','3/4','4/4','3/8','4/8','6/8','9/8','12/8'])
        timeSignatureLabel = QLabel("Time Signature")
        timeSignatureLabel.setBuddy(self.timeSignatureComboBox)
        layout = QGridLayout()
        layout.addWidget(timeSignatureLabel, 0, 0, 1, 1)
        layout.addWidget(self.timeSignatureComboBox,0,1,1,1)
        self.othersGroup.setLayout(layout)
   
    def createPianoRollGroup(self):
        self.pianoRollGroup = QGroupBox("Piano Roll")
        self.pianoRollView = PianoRollView(self.appctxt, None)

        layout = QGridLayout()
        layout.addWidget(self.pianoRollView, 0, 0)
        self.pianoRollGroup.setLayout(layout)
    def createStaffGroup(self):
        # TODO This thing here needs to create as many staffs as the players (or the given conditioned voices)
        self.staffGroup = QGroupBox("Staff", self)
        self.staffView = StaffView(appctxt = self.appctxt, parent=self)
        self.humanLabel = QLabel("H")
        self.humanLabel.setObjectName("Human")
        self.machineLabel = QLabel("M")
        self.machineLabel.setObjectName("Machine")
        layout = QGridLayout()
        layout.addWidget(self.staffView, 0, 1, 6,150)
        layout.addWidget(self.humanLabel, 2,0, 1, 1 , Qt.AlignTop)
        layout.addWidget(self.machineLabel, 4,0,1,1, Qt.AlignTop)
        #layout.addWidget(self.staffView, 0, 0)
        self.staffGroup.setLayout(layout)

    def setupThreads(self):
        #TODO 
        self.currentAudioFrame = Queue()
        self.currentAudioNote = Queue()
        self.currentAudio2MidiEvent = Queue()
        
        # Each player has a sync and async module related to them. 
        # Sync modules operate in sync with the clock
        # Async operate according to a timer (way faster than the clock signal)
        # or according to signals from other modules (besides clock)

        for player in self.players:
            if player.type in ['human', 'human2']:
                # for humans the async module is MidiKeyboardReaderAsync that reads 
                # the input from the midi keyboard, or the keyboard of the laptop
                # the notes are stored in either the keyboardBuffer (laptop keyboard)
                #  or the asyncQueue (midi keyboard)
                tempKeyboardBuffer = Queue()
                tempAsyncQueue = Queue()
                tempAsync = MidiKeyboardReaderAsync( tempAsyncQueue, tempKeyboardBuffer, player)
                
                # there is not thread for the async module of human players
                # (MidiKeyboardReaderAsync) since it uses a timer to run periodicaly 
                # on the background
                tempAsyncThread = None
                # for human players, the sync module is MidiReaderSync(), which 
                # reads the input from tempAsyncQueue
                tempSyncThread = QThread()
                tempSync = MidiReaderSync(currentMidiKeyboardNote = tempAsyncQueue,  
                                            currentAudio2MidiEvent = self.currentAudio2MidiEvent,
                                            parentPlayer = player)
                tempSync.moveToThread(tempSyncThread)
            elif player.type in ['machine', 'machine2']:
                # for machine, the async module is the GeneratorDNN(), which is the neural net.
                # The neural predicts a note on evey 16th note, but, in order to do so, it needs 
                # the last note the human played, so NeuralNet's run function is triggered by
                #  the signal that MidiReaderSync emits and not the Clock() signal.
                tempKeyboardBuffer = None
                tempSyncThread = QThread()
                # GeneratorDNN() pushes the generated notes in the tempAsyncQueue
                tempAsyncQueue = Queue()
                # Similar to the MidiReaderSync(), NeuralNetSync(), operates in sync with the clock
                # and reads the neural net generated notes from the tempAsyncQueue
                tempSync = NeuralNetSync(tempAsyncQueue, player)
                tempSync.moveToThread(tempSyncThread)
                tempAsyncThread = QThread()
                tempAsync = NeuralNet(tempAsyncQueue, 
                                         self.notesDict, self.appctxt, 
                                         parentPlayer = player, parent = self)
                tempAsync.moveToThread(tempAsyncThread)
            elif player.type == 'metronome':
                # for metronome, things are simpler. There is only a sync module
                # which is the Metronome
                tempKeyboardBuffer = None
                tempSyncThread = QThread()
                tempSync = Metronome(appctxt = self.appctxt, parentPlayer = player, parent = self)
                tempSync.moveToThread(tempSyncThread)
                tempAsync = None
                tempAsyncThread = None
            elif player.type == 'condition':
                # In the future, there will be another type of player wich will be static
                # for example, a given chord sequence, or a given melodic line
                raise NotImplementedError
            modules = {
                    "keyboardBuffer" : tempKeyboardBuffer, 
                    "asyncModule" : tempAsync,
                    "asyncThread" : tempAsyncThread,
                    "asyncQueue" : tempAsyncQueue,
                    "syncModule" : tempSync,
                    "syncThread" : tempSyncThread
                    }
            player.modules = modules
            #print(player.__dict__)

        # Manager Thread
        self.threadManager = QThread()
        self.manager = Manager(self.params, self.players, parent = self) # self.midiOut, 
        self.manager.moveToThread(self.threadManager)

        # Memory Thread
        self.threadMemory = QThread()
        self.memory = Memory(parent = self, notesDict = self.notesDict, 
                                    experimentPath = self.experimentPath)
        self.memory.moveToThread(self.threadMemory) 

        # Tempo Estimator
        #TODO not used for now
        # self.threadTempoEstimator = QThread()
        # self.tempoEstimator = TempoEstimator(self.params)
        # self.tempoEstimator.moveToThread(self.threadManager)

        # Clock
        self.threadClock = QThread()
        self.clock = Clock(self.appctxt)
        self.clock.moveToThread(self.threadClock)

        # start all the threads of the sync and async modules of each player
        for player in self.players:
            if player.modules['syncThread'] is not None:
                player.modules['syncThread'].start()
            if player.modules['asyncThread'] is not None:
                player.modules['asyncThread'].start()
        # as long as the clock thread starts, send a signal to activate 
        # its run method
        self.threadClock.started.connect(self.clock.run1)
        # start the rest of the modules
        self.threadClock.start()
        # self.threadTempoEstimator.start()
        self.threadManager.start()
        self.threadMemory.start()

    def signalsNslots(self):

        humanPlayers = [player for player in self.players if player.type in ['human', 'human2']]
        machinePlayers = [player for player in self.players if player.type in ['machine', 'machine2']]
        metronomePlayer = [player for player in self.players if player.type == 'metronome'][0]

        for humanPlayer in humanPlayers:
            # actions in the human player tab of preferences box, trigger signals that call
            # the method self.changeAttribute, with the appropriate arguments
            humanPlayer.preferencesTab.directMonBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'directMonFlag'))#, extra = humanPlayer.preferencesTab.directMonBox.isChecked()))
            humanPlayer.preferencesTab.queueMidiEventsBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'queueMidiEvents'))#, extra = humanPlayer.preferencesTab.queueMidiEventsBox.isChecked()))
            humanPlayer.preferencesTab.keyboardInpBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'internalKeyboardFlag'))#, extra = humanPlayer.preferencesTab.keyboardInpBox.isChecked()))
            humanPlayer.preferencesTab.channelInBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'channelIn'))
            humanPlayer.preferencesTab.channelOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'channelOut'))
            humanPlayer.preferencesTab.midiOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'defaultMidiOut'))
            humanPlayer.preferencesTab.midiInBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'defaultMidiIn'))
            humanPlayer.preferencesTab.refreshMidiButton.pressed.connect(self.updatePortsDict)
            # as I mentioned before, every human's sync module, emmits a signal (midiReaderOutputSignal)
            # in order to inform  the machine player(s) about the new notes the human(s) played
            for machinePlayer in machinePlayers:
                humanPlayer.modules['syncModule'].midiReaderOutputSignal.connect(machinePlayer.modules['asyncModule'].forwardPass)
            
            # human's sync module also sends every new note to the Manager()'s receiver method
            humanPlayer.modules['syncModule'].midiReaderOutputSignal.connect(self.manager.receiver)
            
            # the line below is not currently used. But when we ll add real time beat tracking
            # the async module of humanPlayer will measure the time between MIDI events, and will
            # inform the TempoEstimator() module to calculate the current BPM speed
            # humanPlayer.modules['asyncModule'].sendDurToEstimatorSignal.connect(self.tempoEstimator.dur2bpm)
            
            # connect the signal the clock emits with all the human sync modules
            self.clock.clockSignal.connect(humanPlayer.modules['syncModule'].getNewMidiEvent)

        for machinePlayer in machinePlayers:
            
            self.toolbar.reset.triggered.connect(machinePlayer.modules['asyncModule'].initHiddenStates)

            # human's sync module also sends every new note to the Manager()'s receiver method
            machinePlayer.modules['syncModule'].neuralNetSyncOutputSignal.connect(self.manager.receiver)

            # currently not in use
            # self.toolbar.condition.triggered.connect(machinePlayer.modules['asyncModule'].loadConditionFile)
            
            # when we have more than one machine player, each note that a machine player generates
            # has to sent to all the other machine players also
            for machinePlayerOther in machinePlayers:
                if machinePlayerOther.name != machinePlayer.name :
                    machinePlayer.modules['syncModule'].neuralNetSyncOutputSignal.connect(machinePlayerOther.modules['asyncModule'].forwardPass)
            
            # connect the signal the clock emits with all the machine sync modules
            self.clock.clockSignal.connect(machinePlayer.modules['syncModule'].getNewNeuralNetPrediction)
            
            # actions in the machine player tab of preferences box, trigger signals that call
            # the method self.changeAttribute, with the appropriate arguments
            machinePlayer.preferencesTab.channelOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'channelOut'))
            machinePlayer.preferencesTab.tempBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'temperature'))
            machinePlayer.preferencesTab.refreshMidiButton.pressed.connect(self.updatePortsDict)
            machinePlayer.preferencesTab.midiOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'defaultMidiOut'))
            
            # TODO this is not correct for the case I have two machine players
            # machinePlayer.tool.tempBox.hit.connect(lambda state, extra, name: self.changeAttribute(state, extra, name, 'temperature'))
            #self.toolbar.randomnessSlider.valueChanged.connect(self.fixThat)
            # self.mixer.metronomeSlider.volumeSlider.valueChanged.connect(self.updateVolumes)

        # we ll have only one metronome player, so no need for for loop
        metronomePlayer.modules['syncModule'].metronome2managerSignal.connect(self.manager.receiver)
        metronomePlayer.preferencesTab.channelOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'channelOut'))
        metronomePlayer.preferencesTab.firstPitchBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'pitch1'))
        metronomePlayer.preferencesTab.otherPitchBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'pitch2'))
        metronomePlayer.preferencesTab.refreshMidiButton.pressed.connect(self.updatePortsDict)
        metronomePlayer.preferencesTab.midiOutBox.hit.connect(lambda state, extra, player: self.changeAttribute(state, extra, player, 'defaultMidiOut'))
        
        # again, currently tempoEstimator is not used, but when it does, we want it to update
        # the Clock() with the new BPM estimation
        # self.tempoEstimator.updateTempoSignal.connect(self.sendNewBpmVal)

        # connect the signal the clock emits with the metronome sync module
        self.clock.clockSignal.connect(metronomePlayer.modules['syncModule'].process) 

        # manager's signals connect with updatePlot(pianoroll) and memory
        # self.manager.updatePianoRollPainter.connect(self.pianoRollPainter.updatePlot)
        self.manager.updateMemorySignal.connect(self.memory.getNewNoteEvent)

        #self.threadAudio2MidiEvents.started.connect(self.audio2MidiEvents.process)
        #self.threadPitchEstimator.started.connect(self.pitchEstimator.process)

        # Staff signals
        # ctrlSignal is emitted when I press ctrl. StaffView() needs the ctrl events
        # in order to know when the user wants to zoom or slide the staves
        self.ctrlSignal.connect(self.staffView.ctrlKeyReceiver)
        
        # We want the staff related threads to begin after the staffView is ready,
        # so when StaffView() is ready, it emits a signal which connects to the method
        # setupDelayedThreadsAndSignals which starts the staff related threads
        self.staffView.startStaffPainterSignal.connect(self.setupDelayedThreadsAndSignals)

        # Toolbar signals
        self.toolbar.playPause.triggered.connect(self.pauseResumeClock)
        self.toolbar.reset.triggered.connect(self.reset)
        self.toolbar.bpmBox.valueChanged.connect(self.sendNewBpmVal)
        self.toolbar.save.triggered.connect(self.memory.saveHistory)
        self.toolbar.preferences.triggered.connect(self.preferences.showWindow)
        
        # self.toolbar.enforce.triggered.connect(self.enforceSignal)
        # self.toolbar.clear.triggered.connect(self.clearScene)
        
        # MenuBar Signal
        self.menuBar.showMixerAction.triggered.connect(self.mixer.showWindow)
        self.menuBar.quitAction.triggered.connect(self.quit)
        #self.menuBar.preferencesAction.triggered.connect(self.preferences.showWindow)
        self.menuBar.aboutAction.triggered.connect(self.about)
        self.menuBar.aboutQtAction.triggered.connect(self.aboutQt)

    
    @pyqtSlot()
    def setupDelayedThreadsAndSignals(self):
        #TODO staffPainter() is not a thread. If I move it to a thread
        # as I do with all the other modules, I get an error. Currently 
        # the staffPaintin processes run in the main thread.

        # self.threadStaffPainter = QThread()
        self.staffPainter = StaffPainter(staffView = self.staffView, notesDict = self.notesDict, 
                                                appctxt = self.appctxt)
        # self.staffPainter.moveToThread(self.threadStaffPainter)

        self.staffPainter.sendNoteItemToMain.connect(self.staffView.updateStaffView)
        self.manager.updateStaffPainter.connect(self.staffPainter.getNewNoteEvent)
        self.staffView.updatePaintersRectSignal.connect(self.staffPainter.viewChanged)
        self.toolbar.reset.triggered.connect(self.staffPainter.resetEvent)

        self.threadPianoRollPainter = QThread()
        self.pianoRollPainter = PianoRollPainter(self.pianoRollView, self.appctxt)
        self.pianoRollPainter.moveToThread(self.threadPianoRollPainter)
        
        self.manager.updatePianoRollPainter.connect(self.pianoRollPainter.updatePlot)

        self.threadPianoRollPainter.start()
        # self.threadStaffPainter.start()


    @pyqtSlot(object, str, str, object)
    def changeAttribute(self, state, extra, player, attribute):
        print(f"name {player.name} state {state} attribute {attribute} extra {extra}  enableMidiKeyb {player.enableMidiKeyb}")
        if 'channel' in attribute:
            state += 143
        if 'defaultMidiIn' in attribute:
            self.connectToNewMidiInput(state , player)
        elif 'defaultMidiOut' in attribute:
            self.connectToNewMidiOutput(state , player)
        else:
            if extra is None : 
                setattr(player, attribute, state)
            else:
                setattr(player, attribute, extra)
        #player.directMonFlag = player.directMonFlag ^ True
        #self.directMonitorFlag = self.directMonitorFlag ^ True
        #self.directMonSignal.emit(self.directMonitorFlag)

    def updateGrid(self):
        #TODO
        raise NotImplementedError

    def updatePortsDict(self):
        self.midiInDict = {"":-1}
        self.midiOutDict = {"":-1}
        self.usedMidiInPorts = {}
        self.usedMidiOutPorts = {}
        #TODO delete these
        tempMidiIn = rtmidi.MidiIn()
        tempMidiOut = rtmidi.MidiOut() 
        portsNumberInp = range(tempMidiIn.get_port_count())
        portsNumberOut = range(tempMidiOut.get_port_count())
        for i in portsNumberInp:
            portName = tempMidiIn.get_port_name(i)
            #print(self.midiIn.get_port_name(i))
            self.midiInDict[portName] = i
        for i in portsNumberOut:
            portName = tempMidiOut.get_port_name(i)
            #print(self.midiOut.get_port_name(i))
            self.midiOutDict[portName] = i
        #print(self.midiInDict.keys())
        #print(self.midiOutDict.keys())
        for player in self.players:
            player.midiOut.close_port()
            player.preferencesTab.midiOutBox.clear()
            player.preferencesTab.midiOutBox.addItems(self.midiOutDict.keys())
            if 'human' in player.type:
                player.midiIn.close_port()
                player.preferencesTab.midiInBox.clear()
                player.preferencesTab.midiInBox.addItems(self.midiInDict.keys())
    def openDefaultPorts(self):
        outPorts = list(self.midiOutDict.items())
        inPorts = list(self.midiInDict.items())
        print(outPorts)
        print(inPorts)
        for player in self.players:
            if player.defaultMidiOut is not None:
                defaultOutInd = [port[1] for port in outPorts if player.defaultMidiOut in port[0]]
                
                if len(defaultOutInd) > 0:
                    player.preferencesTab.midiOutBox.setCurrentIndex(defaultOutInd[0]+1)
                    self.connectToNewMidiOutput(defaultOutInd[0]+1, player)
            if 'human' in player.type:
                if player.defaultMidiIn is not None:
                    defaultInInd =  [port[1] for port in inPorts  if player.defaultMidiIn  in port[0]]
                    if len(defaultInInd) > 0:
                        player.preferencesTab.midiInBox.setCurrentIndex(defaultInInd[0]+1)
                        self.connectToNewMidiInput(defaultInInd[0]+1, player)
  
    # currently not in use
    # @pyqtSlot(int)
    # def fixThat(self,value):
    #     machinePlayers = [player for player in self.players if player.type in ['machine', 'machine2']]
    #     for machinePlayer in machinePlayers:
    #         machinePlayer.preferencesTab.tempBox.setValue(value)
    
    
    def connectToNewMidiInput(self, portInd, player):
        # print("___________________________________________________________")
        if portInd > 0:
            if portInd-1  in list(self.usedMidiInPorts.keys()):
                # maybe a MIDI port is already open and in use by another 
                # player, so in this case opening again the same port would 
                # cause an error. 
                player.midiIn = self.usedMidiInPorts[portInd-1]
            else:
                # if the MIDI port is not already in use, then open it and 
                # assign it to the player
                temp = rtmidi.MidiIn()
                temp.open_port(portInd-1)
                player.midiIn = temp
                self.usedMidiInPorts[portInd-1] = temp
    @pyqtSlot(int)
    def connectToNewMidiOutput(self, portInd, player):
        # print("___________________________________________________________")
        if portInd > 0:
            # print(f"++++++++++++{player.name} {portInd} and  {list(self.usedMidiOutPorts.keys())}")
            if portInd-1  in list(self.usedMidiOutPorts.keys()):
                # maybe a MIDI port is already open and in use by another 
                # player, so in this case opening again the same port would 
                # cause an error. 
                player.midiOut = self.usedMidiOutPorts[portInd-1]
            else:
                # if the MIDI port is not already in use, then open it and 
                # assign it to the player
                temp = rtmidi.MidiOut()
                temp.open_port(portInd-1)
                player.midiOut = temp
                print(temp.is_port_open())
                print(player.midiOut.is_port_open())
                self.usedMidiOutPorts[portInd-1] = temp
    
    # currently not used
    @pyqtSlot(str)
    def setTimeSignature(self, value):
        #TODO thats not good practice, I shouldn't communicate directly with self.clock
        # but I should do it through signals/slots. But since I am running a while loop 
        # on self.clock.run1, the event loop is blocked, so no signal/slot are received
        self.clock.setTimeSignature(value)
    
    @pyqtSlot()
    def sendNewBpmVal(self):
        value = self.toolbar.bpmBox.value()
        print(f" bpmBox valueChanged signal activated {value}")
        #TODO thats not good practice, I shouldn't communicate directly with self.clock
        # but I should do it through signals/slots. But since I am running a while loop 
        # on self.clock.run1, the event loop is blocked, so no signal/slot are received
        self.clock.changeBpm(value)

    #@pyqtSlot()
    def pauseResumeClock(self):
        #TODO thats not good practice, I shouldn't communicate directly with self.clock
        # but I should do it through signals/slots. But since I am running a while loop 
        # on self.clock.run1, the event loop is blocked, so no signal/slot are received
        self.clock.pauseResumeClock()
        if self.clock.paused:
            self.sendMidiOffEvents()
            self.toolbar.playPause.setIcon(QtGui.QIcon(self.appctxt.get_resource("Images/svg/play.svg")))
        else :
            self.toolbar.playPause.setIcon(QtGui.QIcon(self.appctxt.get_resource("Images/svg/pause.svg")))

    # currently not used
    @pyqtSlot()
    def clearScene(self):   
        self.toolbar.playPause.trigger()
        self.staffView.staffScene.clear()
        self.staffView.horizontalScrollBar().setValue(0)
        self.staffView.addStaffs()
        self.plotDataDnn = []
        self.plotCurve1.clear()
        self.plotCurve2.clear()
        self.plotCurve1.cl
        #del self.staffScene
        #del self.staffLines
        #print(self.horizontalScrollBar().value())
        # print(self.parent.staffPainter.svgTreble)
        #self.staffScene.addItem(self.staffLines)
    @pyqtSlot()
    def reset(self):
        #TODO if already paused, do not trigger
        # also keep in mind that QAction.trigger() is already a slot in C++
        self.toolbar.playPause.trigger()
        self.toolbar.save.trigger()

        #TODO thats not good practice, I shouldn't communicate directly with self.clock
        # but I should do it through signals/slots. But since I am running a while loop 
        # on self.clock.run1, the event loop is blocked, so no signal/slot are received
        self.clock.reset()
        
    @pyqtSlot()
    def about(self):
        #msg = QString("We must be <b>bold</b>, very <b>bold</b>")
        with open(self.appctxt.get_resource("about.html"),"r") as aboutFile:
            aboutTxt = aboutFile.read()
        QMessageBox.about(self, "About", aboutTxt)# "BachDuet: A Human-Machine Duet Improvisation System\n")
    @pyqtSlot()
    def aboutQt(self):
        QMessageBox.aboutQt(self, "About Qt")
    
    @pyqtSlot()
    def quit(self):
        QApplication.quit()
        #sys.exit()
    
    def closeEvent(self, event):
        #TODO thats not good practice, I shouldn't communicate directly with self.clock
        # but I should do it through signals/slots. But since I am running a while loop 
        # on self.clock.run1, the event loop is blocked, so no signal/slot are received
        self.clock.stopit()
        
        for player in self.players:
            if player.type == 'human':
                player.modules['asyncModule'].stopit()
            if player.type in ['machine']:
                #TODO replace this with signal and slot
                player.modules['asyncModule'].hidden2pickle()
        self.memory.saveHistory()
        #self.logger.info("MESSAGE FROM LOGGER _ CLOSEEEED")
        #self.audioRecorder.stopit()
        #self.pitchEstimator.stopit()
        #self.audio2MidiEvents.stopit()
        #self.keyboardReaderAsync.stopit()
        self.sendMidiOffEvents()
        #self.deleteLater() 

    def sendMidiOffEvents(self):
        time.sleep(1)
        for i in range(128):
            for player in self.players:
                player.midiOut.send_message([player.channelOut, i, 0])

    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if not eventQKeyEvent.isAutoRepeat():
            if key == Qt.Key_Control:
                self.ctrlPressed = True
                self.ctrlSignal.emit("press")
            try:
                aaa =  KeyMappings[key]
                #print(KeyMappings[key])
                #print(f"line 724 in main {KeyMappings[key]}  ctrl {self.ctrlPressed}")
                if self.ctrlPressed is False:
                
                    # self.internalKeyboardAsyncBuffer.put([self.players[0].channelIn, aaa, 127])
                    for player in self.players:
                        if player.type in ['human','human2']:
                            #print(f"internalKeyb flag for {player.type} is {player.internalKeyboardFlag}")
                            if player.internalKeyboardFlag is True:
                                player.modules['keyboardBuffer'].put([player.channelIn, aaa, 127])
                    # [player.modules['keyboardBuffer'].put([player.channelIn, aaa, 127]) for player in self.players if player.type in ['human', 'human2']]
                    #print(f"self.ctrlPressed {self.ctrlPressed} kai meta id ouras = {id(self.internalKeyboardAsyncBuffer)} with codent {self.internalKeyboardReaderAsync.queue}")
            except Exception as e:
                print(f"exception {e} and key is {key}")
                pass
            if self.ctrlPressed is True:
                if key == Qt.Key_E:
                    self.enforceSignal.emit()
                    #print(f"patisa EEEE")
            if key == Qt.Key_Right:
                for player in self.players:
                    if player.type in ["machine", "machine2"]:
                        player.modules['asyncModule'].saveHiddenStates(label = 1)
            if key == Qt.Key_Left:
                for player in self.players:
                    if player.type in ["machine", "machine2"]:
                        player.modules['asyncModule'].saveHiddenStates(label = 0)

                        
            
                
            #print('released')
    def keyReleaseEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if not eventQKeyEvent.isAutoRepeat():
            if key == Qt.Key_Control:
                self.ctrlPressed = False
                self.ctrlSignal.emit("release")
            try:
                aaa =  KeyMappings[key]
                
                if self.ctrlPressed is False:
                    for player in self.players:
                        if player.type in ['human','human2']:
                            if player.internalKeyboardFlag is True:
                                player.modules['keyboardBuffer'].put([player.channelIn, aaa, 0])
                    # self.internalKeyboardAsyncBuffer.put([self.players[0].channelIn, aaa, 0])
                    # [player.modules['keyboardBuffer'].put([player.channelIn, aaa, 0]) for player in self.players if player.type in ['human', 'human2']]
                    #print(f"self.ctrlPressed {self.ctrlPressed} kai meta id ouras = {id(self.internalKeyboardAsyncBuffer)} with codent {self.internalKeyboardReaderAsync.queue}")
            except:
                pass
def configure_logger(name):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '%(asctime)s.%(msecs)05d %(levelname)s %(module)s - %(funcName)s -%(threadName)s -%(lineno)s: %(message)s', 'datefmt': '%H:%M:%S'}
            
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            'default': {
                'level': 'DEBUG',
                'handlers': ['console']
            }
        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(name)

if __name__ == '__main__':
    logger = configure_logger('default')
    
    CUDA_LAUNCH_BLOCKING=1
    appctxt = ApplicationContext()
    
    styleSheet = appctxt.get_resource("styleSheet.css")
    app = QApplication(sys.argv)
    
    with open(styleSheet,"r") as fh:
        app.setStyleSheet(fh.read())

    bachDuet = BachDuet(appctxt, logger)

    exit_code = app.exec_()   
    sys.exit(exit_code)