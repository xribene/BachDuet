from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
from utils import Params, TensorBuffer, rename
from ParsingClasses import Vocabulary
import pickle, time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import weight_norm
import torch.optim as optim 
from pathlib import Path

class Manager(QObject):
    updatePianoRollPainter = pyqtSignal(int,int)
    updateMemorySignal = pyqtSignal(list)
    updateStaffPainter = pyqtSignal(list)
    def __init__(self, params, players, parent):
        super(Manager,self).__init__()
        self.params = params
        self.parent = parent
        self.players = players
        # self.midiOut = midiOut
        self.masterVolume = 127
        self.currentTick = 0
        # self.key = 'C major'
        self.played = False
        self.meanPlayer1 = 0
        self.meanPlayer2 = 0
        
    # edw mipws na kanw 2 diaforetikous receivers
    @pyqtSlot(dict)
    def receiver(self, output):
        #print(f"manager received {output}")
        for player in self.players:
            if player.name == output['playerName']:
                # if player.type in ['machine']:
                #     self.key = output['keyEstimation']# key 
                if player.type in ['metronome']:
                    self.currentTick = output['tick']
                player.managerFlag = True
                player.nextNote = [output['midi'], output['artic'], output['tick'], output['rhythmToken']]
                player.nextNoteDict = output
                if player.meamMidi == 0:
                    player.meanMidi = player.nextNoteDict['midi']
                else:
                    player.meanMidi = 0.7 * player.meanMidi + 0.3 * player.nextNoteDict['midi']
                break
        # aaa = [player.id for player in self.players]
        conditionShow = False if False in [player.managerFlag for player in self.players ] else  True
        conditionPlay = False if False in [player.managerFlag for player in self.players if player.type in ['metronome','machine']] else True
        
        #print(f"    FLAGS ARE {[str(player.managerFlag) + str(player.name) for player in self.players ]} CONDITION PLAY IS {conditionPlay} CONDITION SHOW IS {conditionShow}")
        if conditionShow :
            self.played = False
            # This thing triggers every sixteen note, since producers send messages all the time, either hit=1 either hit=0 either rest
            
            # check if all the ticks are the same. Their set should have size 1
            
            # assert len(set([player.nextNote[2] for player in self.players])) == 1
            # assert self.nextNoteDnn[2] == self.nextNoteMidiKeyboard[2]
            # assert self.nextNoteDnn[2] == self.nextMetronomeBeep[2] 
            numMachines = len([player.name for player in self.players if player.type in ['machine', 'machine2']])
            numHumans = len([player.name for player in self.players if player.type in ['human','human2']])
            if numMachines == 2:
                # humanNotes = [player.nextNote for player in self.players if player.type == 'human'][0]
                machineNotes = [player.nextNoteDict for player in self.players if player.type  in ['machine','machine2']]
                metronomeNote = [player.nextNoteDict for player in self.players if player.type == 'metronome'][0]
                self.updatePianoRollPainter.emit(machineNotes[0]['midi'],machineNotes[1]['midi'])
                self.updateStaffPainter.emit([machineNotes[0],machineNotes[1], metronomeNote])
                self.updateMemorySignal.emit([machineNotes[0],machineNotes[1], metronomeNote, None])

            elif numHumans == 2:
                humanNotes = [player.nextNoteDict for player in self.players if player.type in ['human','human2']]
                metronomeNote = [player.nextNoteDict for player in self.players if player.type == 'metronome'][0]
                self.updatePianoRollPainter.emit(humanNotes[0]['midi'],humanNotes[1]['midi'])
                self.updateStaffPainter.emit([humanNotes[0],humanNotes[1], metronomeNote])
                self.updateMemorySignal.emit([humanNotes[0],humanNotes[1],  metronomeNote])
            
            elif (numHumans == 1) and (numMachines == 1):
                humanNotes = [player.nextNoteDict for player in self.players if player.type == 'human'][0]
                machineNotes = [player.nextNoteDict for player in self.players if player.type == 'machine'][0]
                metronomeNote = [player.nextNoteDict for player in self.players if player.type == 'metronome'][0]
                self.updatePianoRollPainter.emit(machineNotes['midi'],humanNotes['midi'])
                self.updateStaffPainter.emit([machineNotes,humanNotes, metronomeNote])
                self.updateMemorySignal.emit([machineNotes,humanNotes, metronomeNote])
            else:
                raise EnvironmentError
            for player in self.players:
                player.managerFlag = False
            
        elif conditionPlay and not self.played:
            self.playMidi()
            self.played = True
    def playMidi(self):
        #print(f"INSIDE Player for tick {self.currentTick} at time {time.time()}")
        for player in self.players:
            if player.type == 'metronome':
                if player.nextNote[0] is not None: # einai swsto auto, giati otan den prepei na akoustei stelnei None sto pitch. kalo e  ???? # TODO change index to 0 
                    self.parent.toolbar.lcd.display(self.currentTick//4+1)
                    if player.midiOut is not None:
                        player.midiOut.send_message([player.channelOut, player.nextNote[0], player.volume])
                        #print(f"metronome sound was send to channel {player.channelOut}")
            else :
                if player.directMonFlag is True :
                    continue
                if player.nextNote[1] == 1: #hit
                    if not player.onRest:
                        # if lastNote is still playing, KILL IT
                        # here i use the same channel for noteOn and noteOff
                        # the correct way is to use the correct channels
                        # but for now is ok 
                        if player.muteStatus is False:
                            if player.midiOut is not None:
                                player.midiOut.send_message([player.channelOut ,player.lastNote , 0])
                    if not player.nextNote[0]==0:
                        player.lastMidiEvent = [player.channelOut,player.nextNote[0], player.volume]
                        if player.muteStatus is False:
                            if player.midiOut is not None:
                                player.midiOut.send_message(player.lastMidiEvent)
                        player.lastNote = player.nextNote[0]
                        player.onRest = False
                    else:
                        player.onRest = True
                else:
                    pass
        #print(f"esteila metronome {self.channelMetronome}, dnn {self.channelDnn} human {self.channelMidiKeyboard}")
    # @pyqtSlot(bool)
    # def setMonitoringMode(self, directMonFlag):
    #     self.directMonFlag = directMonFlag   
    @pyqtSlot(bool)
    def setMuteStatusNN(self, nnMuteStatus):
        self.nnMuteStatus = nnMuteStatus  
    @pyqtSlot(bool)
    def setMuteStatusInp(self, inpMuteStatus):
        self.inpMuteStatus = inpMuteStatus    