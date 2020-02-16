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
    """
    Manager class, organizes the outputs of all agents, and ensures everything
    is in sync

    Attributes
    ----------
    players : list(Player())
        a list of the current Player() objects
        involved in the session. 
    parent : QWidget()
        The BachDuet() class

    Signals
    -------
    All the signals below are emitted only after the Manager()
    receives the output from all agents/players (for the current "tick")

    updatePianoRollPainter : pyqtSignal(int,int)
       sends the outputs to the PianoRollPainter() 
    updateMemorySignal : pyqtSignal(list)
        sends the outputs to the Memory() 
    updateStaffPainter : pyqtSignal(list)
        sends the outputs to the StaffPainter() 


    Methods
    -------
    receiver(output) : None
        This slot is connected with signals from all the 
        players/agents, and receives their output (dict)on 
        every clock "tick". 

    playMidi() : None
        This method is called only when the receiver() has 
        all the outputs of all agents/players for the curent "tick"
        end sends these outputs to the correct midi out ports and
        channels. With this way, we make sure the outputs are 
        played simultaneously. (The output of the human players is
        managed by playMidi() only when the flag directMonitoring of 
        the player is False).

    """

    updatePianoRollPainter = pyqtSignal(int,int)
    updateMemorySignal = pyqtSignal(list)
    updateStaffPainter = pyqtSignal(list)

    def __init__(self,  players, parent):
        super(Manager,self).__init__()
        self.parent = parent
        self.players = players
        self.currentTick = 0
        self.played = False
        
    @pyqtSlot(dict)
    def receiver(self, output):
        
        for player in self.players:
            # receiver is triggered by a signal emmited from one of the players
            # we have to find from which one. 
            if player.name == output['playerName']:
                if player.type in ['metronome']:
                    # metronome sets the currentTick
                    self.currentTick = output['tick']
                # when managerFlag is True, it means this player's output 
                # has been accepted from Manager() for the currentTick
                # we use this flag to monitor when we ll receive signal from
                # all players/agents
                player.managerFlag = True
                # keep the output of the player, in the class/object of the
                # same player
                player.nextNoteDict = output
                # we keep a running average of the midi notes of each player
                # we use this later, when we visualize the results in xml
                # to determine the clef for each part/player
                if player.meamMidi == 0:
                    player.meanMidi = player.nextNoteDict['midi']
                else:
                    player.meanMidi = 0.7 * player.meanMidi + 0.3 * player.nextNoteDict['midi']
                break 
        # conditionShow is True only when we have received the output/signal 
        # from all the players/agents and indicates that the receiver() is ready
        #  to emit signals to all the interested modules (pianoRoll,staff,memory)
        conditionShow = False if False in [player.managerFlag for player in self.players ] else  True
        # conditionPlay is True only when we have received the output/signal 
        # from all the players/agents whose directMonitoring flag is False
        # and indicates that the receiver() is ready send all the outputs to playMidi()
        conditionPlay = False if False in [player.managerFlag for player in self.players if player.type in ['metronome','machine']] else True
        
        #print(f"    FLAGS ARE {[str(player.managerFlag) + str(player.name) for player in self.players ]} CONDITION PLAY IS {conditionPlay} CONDITION SHOW IS {conditionShow}")
        if conditionShow :
            self.played = False #TODO check the logic here
            # This thing triggers every sixteen note, since producers send messages all the time, either hit=1 either hit=0 either rest
            
            # check if all the ticks are the same. Their set should have size 1
            
            # assert len(set([player.nextNote[2] for player in self.players])) == 1
            # assert self.nextNoteDnn[2] == self.nextNoteMidiKeyboard[2]
            # assert self.nextNoteDnn[2] == self.nextMetronomeBeep[2] 

            #TODO this was coded in rush. Find a better way in a for loop.
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

            # reset managerFlags back to False
            for player in self.players:
                player.managerFlag = False
            
        elif conditionPlay and not self.played: #TODO check the logic here
            self.playMidi()
            self.played = True
    def playMidi(self):
        #print(f"INSIDE Player for tick {self.currentTick} at time {time.time()}")
        for player in self.players:
            if player.type == 'metronome':
                # Metronome() sends a sound every 4 clock "ticks". 
                # for the rest of them it sends None
                if player.nextNote[0] is not None: 
                    # Here I update the lcd display for the beat, so the 
                    # visual and auditory cues occur simultaneously
                    #TODO maybe move the line below, inside the following
                    # if statement
                    self.parent.toolbar.lcd.display(self.currentTick//4+1)
                    if player.midiOut is not None:
                        player.midiOut.send_message([player.channelOut, player.nextNote[0], player.volume])
                        #print(f"metronome sound was send to channel {player.channelOut}")
            else :
                if player.directMonFlag is True :
                    # in this case, the output of the agent/player is 
                    # managed by its 'async' module, and not by the Manager()
                    continue
                # we are interested only in the onsets. This is ok for monophonic
                # voices. When I receive an onset, all previous notes are stopped
                if player.nextNote[1] == 1: # if onset
                    # first we check the case where the player is not onRest, namely
                    # there is a previous note still played/holded. In this case we have
                    # to send a midi off event first for this note.
                    if not player.onRest:
                        # if player is not muted.
                        if player.muteStatus is False:
                            # if player is connected to a valid output Midi port
                            if player.midiOut is not None:
                                # here i follow the format of Keystation32 where 
                                # the same channel for noteOn and noteOff is used
                                player.midiOut.send_message([player.channelOut ,player.lastNote , 0])
                    # Now, after we stopped the previous notes the player is onRest, so 
                    # we just have to play the new midi on event. 
                    # Remember, the articulation is onset (1), for the rest token also
                    # so we want to make sure this is not a rest.
                    if not player.nextNote[0]==0: # if not rest
                        player.lastMidiEvent = [player.channelOut,player.nextNote[0], player.volume]
                        if player.muteStatus is False:
                            if player.midiOut is not None:
                                player.midiOut.send_message(player.lastMidiEvent)
                        # Update the player's lastNote
                        player.lastNote = player.nextNote[0]
                        # update onRest flag
                        player.onRest = False
                    else:
                        # if the note is rest ...
                        player.onRest = True
                else:
                    # If articulation of the note is 0, then do nothing
                    pass
        #print(f"esteila metronome {self.channelMetronome}, dnn {self.channelDnn} human {self.channelMidiKeyboard}")
   