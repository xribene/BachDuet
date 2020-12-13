from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
import time 

class MidiKeyboardReaderAsync(QObject):
    """
    Module that reads the MIDI input real time

    This module is ascociated with a parent human player, and it reads
    the MIDI input from either a MIDI keyboard, or from the internal keyboard
    of the device (laptop, desktop)

    Attributes
    ----------
    keyboardMidiEventsQueue : Queue()
        The Queue in which it pushes noteOn midi events that reads from a MIDI Keyboard
    internalKeyboardAsyncQueue : Queue()
        This Queue contains all the midi events from the internal keyboard of the device
    parentPlayer : Player()
        The parent human player ascociated with the current instance of the MidiKeyboardReaderAsync
        module. 

    Methods
    -------
    stopit() : None
        stops reading MIDI input
    readMidiInput() : None
        reads input from both input streams (Midi and internal keyboards)
        and pushes the noteOn events in the keyboardMidiEventsQueue Queue()
        Extra steps are taken to ensure that the input is monophonic. 
    getMidiEventInfo(midiEvent, keystation) : list
        Takes a midiEvent as an input and returns 
        the properties 1) eventType : noteOn, noteOff
        2) channel : 0-15, 3) midiNumber : 0-255,
        4) velocity : 0-255
        keystation can be either 0 or 1, depending on whether the input
        is from keyStation32 midi keyboard or not. Generally some keyboards
        sent both noteOn and noteOff events using the same channel, while 
        others use different channels.

    """
    # sendDurToEstimatorSignal = pyqtSignal(float)
    def __init__(self, keyboardMidiEventsQueue, internalKeyboardAsyncQueue, parentPlayer):
        super(MidiKeyboardReaderAsync, self).__init__()
        self.parentPlayer = parentPlayer
        self.params = self.parentPlayer.params
        self.keyboardMidiEventsQueue = keyboardMidiEventsQueue 
        self.internalKeyboardAsyncQueue = internalKeyboardAsyncQueue 

        # Timer that calls readMidiInput every 1 millisecond. 
        self.timer = QTimer()
        self.timer.start(1)
        self.timer.timeout.connect(self.readMidiInput)
        
        self.duration = 0
        self.info = {
            'type' : self.parentPlayer.type,
            'name' : self.parentPlayer.name,
        }

    def stopit(self):
        self.timer.stop()

    def readMidiInput(self):
        # if the receiving input from MIDI keyboard option is enabled,
        # then read the Midi Input. If there is not a MIDI event, 
        # get_message() returns None
        if self.parentPlayer.enableMidiKeyb == True:
            midiEventMidiKeyboard = self.parentPlayer.midiIn.get_message() # some timeout in ms
        else:
            midiEventMidiKeyboard = None
        # Check also if the receiving input from internal keyboard option
        # is enabled, and get the last event if any.
        if self.parentPlayer.internalKeyboardFlag == True:
            try:
                midiEventInternalKeyboard = [self.internalKeyboardAsyncQueue.get(block = False)]
            except :
                midiEventInternalKeyboard = None
        else:
            midiEventInternalKeyboard = None
        
        # Events from MIDI keyboard have higher priority than these from the internal keyboard
        # midiEventAug is the final midi event from either of the two input streams.
        midiEventAug = midiEventMidiKeyboard if midiEventMidiKeyboard is not None else midiEventInternalKeyboard
        
        # if we received a midi event (noteOn or noteOff)
        if midiEventAug is not None:
            timestamp = time.time() # used only for tempoEstimation (not supported yet)
            print(f"{self.parentPlayer.name} midi note received  {midiEventAug}")
            midiEvent = midiEventAug[0]
            # get the properties of the midi event. The procedure to get these can be different
            # from keyboard to keyboard. The method below works for the keyStation 32 midi keyboard
            [midiEventType, midiEventChannel, pitch, velo] = self.getMidiEventInfo(midiEvent, keystation = 0)
            print(f"info extracted {[midiEventType, midiEventChannel, pitch, velo]}")
            

            print(f"{self.parentPlayer.name} channelIn is {self.parentPlayer.channelIn}")
            # Each player listens to a specific port and midi channel. We want to make sure that 
            # the event we received corresponds to the parent player of this instance of the 
            # MidiKeyboardReaderAsync() module.
            if midiEventChannel == self.parentPlayer.channelIn: 
                # If the directMonFlag is True, then we send the midiEvents to the input
                # as soon as we receive them, so the user experiences minimum delay.
                # if directMonFlag is False, then the midiEvent will be played by the Manaer()
                # module, in sync with the clock and the other players (machine, metronome). 
                if self.parentPlayer.directMonFlag:
                    # it is possible to receive a midi event from a channel A,
                    # but sent it to a different output channel B. So we update the 
                    # midi event with the channelOut of the parent player 
                    midiEvent[0] = self.parentPlayer.channelOut
                    self.parentPlayer.midiOut.send_message([self.parentPlayer.channelOut, pitch, velo]) 
                    # keep track of the last Midi event for this player
                    self.parentPlayer.lastMidiEvent = [self.parentPlayer.channelOut, pitch, velo]
                if midiEventType == 'noteOff' :
                    # NOTICE : we do not add noteOff events in the Queue()
                    # I ve used a bit weird logic here (TODO explain this logic)
                    # TODO for a polyphonic version of the system, a better
                    # way has to take consideration of noteOffs. We have to maintain
                    # an structure, with all the MIDI notes, and a active/inactive
                    # flag for each.
                    # TODO Also, for BachDuet v2, there will not be a 16th note
                    # quantization (probably), so we ll have to take in consideration
                    # the noteOff events and calculate the dur of the note

                    ###############################################################
                    ####### UPDATE DURATIONS for TempoEstimator() #################
                    ###############################################################
                    # if self.lastEvent['type'] == 'noteOn':
                    #     if self.lastEvent['note'] == pitch:
                    #         self.duration = timestamp - self.lastEvent['timestamp']
                    #     else:
                    #         pass
                    # elif self.lastEvent['type'] == 'noteOff':
                    #     pass
                    ###############################################################
                    ###############################################################
                    ###############################################################

                    #TODO ignoreNoteOff and holdFlags are very important,
                    # add comments here
                    self.parentPlayer.ignoreNoteOff -= 1
                    if self.parentPlayer.ignoreNoteOff == 0: # if self.ignoreNoteOff is False
                        self.parentPlayer.holdFlag = False

                elif midiEventType == 'noteOn':

                    ###############################################################
                    ####### UPDATE DURATIONS for TempoEstimator() #################
                    ###############################################################
                    # if self.lastEvent['type'] == 'noteOn':
                    #     self.duration = timestamp - self.lastEvent['timestamp']
                    # elif self.lastEvent['type'] == 'noteOff':
                    #     pass
                    ###############################################################
                    ###############################################################
                    ###############################################################

                    # When the user playes notes faster than 16ths, we have two options
                    # either queue these MidiEvents and play them one by one as they
                    # were 16thns, or ignore them.
                    if not self.parentPlayer.queueMidiEvents :
                        # in this case, we want to ignore them, so we make sure, that every
                        # time a new NoteOn event happens, we empty the Queue from any previous
                        # notes. 
                        try:
                            self.keyboardMidiEventsQueue.get(block=False)
                        except:
                            pass
                    # after we empty (or not) the queue from any previous notes, we push the 
                    # new NoteOn event
                    self.keyboardMidiEventsQueue.put([midiEventType, self.parentPlayer.channelOut, pitch])#,self.newNote))
                    #TODO add comments on the idea behind the following lines
                    if self.parentPlayer.holdFlag:
                        self.parentPlayer.ignoreNoteOff += 1 # self.ignoreNoteOff = True
                    else:
                        self.parentPlayer.ignoreNoteOff = 1
                    self.parentPlayer.holdFlag = True
                self.parentPlayer.lastEvent = {'type':midiEventType,
                                  'timestamp':timestamp,
                                  'note':pitch}
                
                # update TempoEstimator with the last time duration between the last
                # two midi events. Not supported yet
                # self.sendDurToEstimatorSignal.emit(self.duration)

    
    def getMidiEventInfo(self, midiEvent, keystation = 1):
        if midiEvent[0] < 144 and midiEvent[0]>127:
            eventType = 'noteOff'
            eventChannel  = midiEvent[0] - 127
        elif midiEvent[0] > 143 and midiEvent[0] < 160:
            eventChannel  = midiEvent[0] - 143 
            if midiEvent[2] == 0:
                eventType = 'noteOff'
            else:
                eventType = 'noteOn'
        else:
            return 'unknown', 0, 0, 0
        eventChannel += 143
        pitch = midiEvent[1]
        velocity = 127 if eventType == 'noteOn' else 0
        return [eventType, eventChannel, pitch, velocity]

class MidiReaderSync(QObject):
    """
    A module that works in sync with the clock, and can reads midi events
    from both the Midi Keyboard or the Audio microphone streams.

    Attributes
    ----------
    keyboardMidiEventsQueue : Queue()
        The queue where MidiKeyboardReaderAsync keeps the keyboard midi events.
        MidiReaderSync picks the last event of this Queue at every clock 'tick'
    audioMidiEventsQueue : Queue()
        The queue where Audio2MidiAsync keeps the midi events which where converted
        from the audio input
    parentPlayer : Player()
        The parent human player ascociated with the current instance of the MidiReaderSync
        module. 

    Signals
    -------
    midiReaderOutputSignal : pyqtSignal()
        This signal is emitted on every 16th note, in sync with the clock
        and it connects with all the machine players, as well as with the Manager()

    Methods
    -------
    getNewMidiEvent(clockTrigger) : None
        a slot that runs on every clockTrigger, and reads the last midi events from 
        either the keyboardMidiEventsQueue or the audioMidiEventsQueue Queues

    """
    midiReaderOutputSignal = pyqtSignal(dict)
    def __init__(self,  keyboardMidiEventsQueue, parentPlayer, audioMidiEventsQueue=None):
        super(MidiReaderSync,self).__init__()
        self.parentPlayer = parentPlayer
        self.params = self.parentPlayer.params 
        self.keyboardMidiEventsQueue = keyboardMidiEventsQueue 
        self.audioMidiEventsQueue = audioMidiEventsQueue

        # TODO don't keep output in a self variable. remember the problem with self.history
        # for now, I ve fixed this problem using deepcopy.copy in the Memory() module
        # the following output dictionary is a template which is filled with different values 
        # every time the process method runs (on each clock 'tick')
        self.output = { 
            "playerName" : self.parentPlayer.name, 
            # the keyEstimation is not used here. We keep it only for compatibility
            # with the neural networks module output
            "keyEstimation" : None, 
            "midi" : None,
            "artic": 0,
            "tick": 0,
            "globalTick" : 0,
            "rhythmToken": None
        }

        # inputMidiSource can be either the Midi Keyboard, or Audio input
        # TODO get it from attributes of parentPlayer
        self.inputMidiSource = 'Midi Keyboard' 
        # self.inputMidiSource = 'Audio Mic'

    @pyqtSlot(dict) 
    def getNewMidiEvent(self,  clockTrigger):

        metronomeBPM = clockTrigger['metronomeBPM']
        # This line is very important here. #TODO add comments
        self.parentPlayer.modules['syncThread'].msleep(int(60/metronomeBPM/4/2*1000))

        tick = clockTrigger['tick']
        rhythmToken = clockTrigger['rhythmToken']
        globalTick = clockTrigger['globalTick']
        if self.inputMidiSource == 'Midi Keyboard':
            try:
                [midiEventType, midiEventChannel, midiEventPitch] = self.keyboardMidiEventsQueue.get(block=False)
                if midiEventType == 'noteOn' : 
                    # It is always 'noteOn' since MidiKeyboardReaderAsync doent push noteOFF 
                    # events in the Queue
                    self.parentPlayer.lastNote = midiEventPitch
                    # SEND TO HUMAN Bus , midiNumber, hit, tick
                    # we use tick for synchronization with the DNN output
                    self.output['midi'] = midiEventPitch
                    self.output['artic'] = 1
            except:
                # If we have an exception, it means that there is not noteOn event on the Queue
                # so either we have rest, or the last note is keep playing (holdFlag == True)
                if self.parentPlayer.holdFlag:
                    # here articulation is 0, because it is a note that is holded
                    # so the midi number of the current 16th note will be the same as the last one
                    self.output['midi'] = self.parentPlayer.lastNote
                    self.output['artic'] = 0
                else:
                    # here it means that we have a rest. The symbol for the rest os '0_1' 
                    # meaning midi=0 and articulation=1
                    # set the correct rest symbol, maybe zero (for DNN is '0_1'=106) # TODO remove this comment (?)
                    self.output['midi'] = 0
                    self.output['artic'] = 1
        
        elif self.inputMidiSource == 'Audio Mic':
            # There are some differences here compared to the 'Midi Keyboard' if branch
            # because, Audio2MidiEvents() sends different type of events compared to 
            # MidiKeyboardReaderAsync(). These differences originate from the fact that 
            # the PitchEstimator() that Audio2MidiEvents() uses assumes monophonic imput only
            # while the RtMIDI() interface that MidiKeyboardReaderAsync() uses, can work
            # with polyphonic inputs. 
            # 'Midi Keyboard' works with the hold flag, and midiKeyboardAsync doesn't send rest events.
            # However , Audio2MidiEvent, sends also restEvents(as noteOn), so I know that whenever 
            #the queue is empty then, I send the previous note as hold=0 (for rest its always 1)
           
            #print(f"AUDIO QUEUE SIZE IS {self.audioMidiEventsQueue.qsize()}")
            try:
                [midiEventType, midiEventChannel, midiEventPitch] = self.audioMidiEventsQueue.get(block=False)
                if midiEventType == 'noteOn' : 
                    # It always enters this 'if', since Audioreader doent sent noteOFF for now
                    self.parentPlayer.lastNote = midiEventPitch
                    self.output['midi'] = midiEventPitch
                    self.output['artic'] = 1

            except:
                # Exception means empty queue, so the previous note is holded
                # --> articulation is 0 (except if the note was rest, then artic=1)
                self.output['midi'] = self.parentPlayer.lastNote
                if self.parentPlayer.lastNote == 0:
                    self.output['artic'] = 1
                else:
                    self.output['artic'] = 0
                # self.send2BusMidiKeyboard = [None, self.parentPlayer.lastNote, hold, tick, rhythmToken]
        self.output['tick'] = tick
        self.output['rhythmToken'] = rhythmToken
        self.output['globalTick'] = globalTick

        self.midiReaderOutputSignal.emit(self.output) 
        #print(f"human Sync emits signal to manager {self.output} at tick {tick} at time {time.time()}")
