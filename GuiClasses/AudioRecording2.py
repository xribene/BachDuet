# -*- coding: utf-8 -*-
"""
Created on Sun May 19 05:08:43 2019

@author: xribene
"""

import pyaudio
import wave
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
import scipy.io.wavfile
import scipy.io
import numpy as np
# import matplotlib.pyplot as plt
import time
from queue import Queue
from collections import deque
import sys


class Audio2MidiEvents(QObject):
    '''  
        similar functionality with MidiKeyboardReaderAsync()
        but for Audio Inputs     
        
    '''
    def __init__(self, pitchEstimationsQueue, audioMidiEventsQueue, parentPlayer):
        super(Audio2MidiEvents, self).__init__()
        self.pitchEstimationsQueue = pitchEstimationsQueue # the result of the pitch estimation is stored here
        self.audioMidiEventsQueue = audioMidiEventsQueue # the 
        self.parentPlayer = parentPlayer
        self.stop = False
        self.lastNote = '' # here use self.parentPlayer.lastMidiEvent instead or self.parentPlayer.lastNote (careful with the last one)
    def stopit(self):
        self.stop = True
    @pyqtSlot(int)
    def process(self, data):
        # TODO consider making the logic similar to MidiKeyboardReaderAsync()
        # because this module it is not actual Audio2Midi. We need NoteOff events
        
        print(f"DATA IS {data}")
        if data != self.lastNote: #
            # if self.lastNote != 0:
            #     pass
            #     #print([144,self.lastNote, 0])
            if data >=0:
                #print([144,data,127])
                if not self.parentPlayer.queueMidiEvents :
                    # in this case, we want to ignore them, so we make sure, that every
                    # time a new NoteOn event happens, we empty the Queue from any previous
                    # notes. 
                    try:
                        self.audioMidiEventsQueue.get(block=False)
                    except:
                        pass
                
                self.audioMidiEventsQueue.put(['noteOn', self.parentPlayer.channelOut, data])#,self.newNote))
                print(['noteOn', self.parentPlayer.channelOut, data])
            else:
                print("data was negative ")
                raise Exception
            self.lastNote = data


class AudioRecorder(QObject):
    audioRecorderSignal = pyqtSignal(bytes)
    def __init__(self, audioFramesQueue, parentPlayer, chunk = 2048, channels = 1, rate = 8000, output_name = "outputClass.wav" ):
        super(AudioRecorder, self).__init__()
        self.parentPlayer = parentPlayer
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = channels
        self.RATE = rate
        self.WAVE_OUTPUT_FILENAME = output_name
        self.audioFramesQueue = audioFramesQueue
        
        self.stopped = True
        print("AudioRecorder INIT")
        
    def openStream(self):
        # self._stream = self._audio.open(
        # format=self.pyaudio_format,
        # channels=self.num_channels,
        # rate=self._raw_audio_sample_rate_hz,
        # input=True,
        # output=False,
        # frames_per_buffer=self.frames_per_chunk,
        # start=True,
        # stream_callback=self._enqueue_raw_audio,
        # **kwargs)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                         input_device_index=0,
                         channels=self.CHANNELS,
                         rate=self.RATE,
                         input=True,
                         frames_per_buffer=self.CHUNK)
        self.frames = []
        self.stopped = False
        self.startTimer()
    def startTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.recordara)
        self.timer.start(int(self.CHUNK*1000/self.RATE))
        #self.timer.start(100)
    @pyqtSlot(str)
    def stopStartRecorder(self, inputSource):
        if inputSource == 'Audio Mic':
            self.openStream()
            
        elif inputSource == 'Midi Keyboard':
            self.stopit()
    def recordara(self):
        # print("recording")
        data = self.stream.read(self.CHUNK)
        # print(data.__class__)
        self.audioRecorderSignal.emit(data)
        self.audioFramesQueue.put(data)
        self.frames.append(data)
    def stopit(self):
        if not self.stopped:
            self.timer.stop()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.saveRecording()
        print("stop recording")
    def saveRecording(self):
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

class TryApp(QObject):
    def __init__(self , parent = None):
        super(TryApp, self).__init__(parent)
        self.audioFramesQueue = Queue()
        self.pitchEstimationsQueue = Queue()
        self.audioMidiEventsQueue = Queue()
        self.stopTimer = QTimer(timeout=self.killAll, singleShot=True)
        self.stopTimer.start(20000)
        self.startProc()
    def startProc(self):
        self.audioRecorder = AudioRecorder(audioFramesQueue = self.audioFramesQueue, parent=self, chunk = 1*1024 )
        self.audioRecorder.stopStartRecorder('Audio Mic')

        self.threadPitchEstimator = QThread()
        self.pitchEstimator = YinEstimator(audioFramesQueue = self.audioFramesQueue, parent=None, pitchEstimationsQueue = self.pitchEstimationsQueue,  harmoThresh=0.15, medianOrder=3)
        self.pitchEstimator.moveToThread(self.threadPitchEstimator)

        self.threadAudio2MidiEvents = QThread()
        self.audio2MidiEvents = Audio2MidiEvents(pitchEstimationsQueue = self.pitchEstimationsQueue, audioMidiEventsQueue = self.audioMidiEventsQueue, parent=None)
        self.audio2MidiEvents.moveToThread(self.threadAudio2MidiEvents)

        self.threadPitchEstimator.started.connect(self.pitchEstimator.process)
        self.threadPitchEstimator.start()
        self.threadAudio2MidiEvents.started.connect(self.audio2MidiEvents.process)
        self.threadAudio2MidiEvents.start()
        
        
    def killAll(self):
        print("KILLALL")
        self.audioRecorder.stopit()
        self.audioRecorder.saveRecording()
        QApplication.quit()

if __name__ == '__main__':
    from queue import Queue
    from collections import deque
    import sys
    
    app = QApplication(sys.argv)
    gallery = TryApp()
    app.exec_()
    #gallery.show()
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QApplication.instance().exec_()
    #audioRecorder = AudioRecorder(audioFramesQueue = audioFramesQueue, chunk = 2048 )
    
#    threadPitchEstimator = QThread()
#    pitchEstimator = YinEstimator(audioFramesQueue = audioFramesQueue, pitchEstimationsQueue = pitchEstimationsQueue)
#    pitchEstimator.moveToThread(threadPitchEstimator)
#
#    threadAudioRecorder.start()
    #threadPitchEstimator.start()
