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

class AudioRecorder(QObject):
    def __init__(self, currentAudioFrame, parent=None, chunk = 4096, channels = 1, rate = 44100, output_name = "outputClass.wav" ):
        super(AudioRecorder, self).__init__(parent)
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self.WAVE_OUTPUT_FILENAME = output_name
        self.currentAudioFrame = currentAudioFrame
        
        self.stopped = True
        print("AudioRecorder INIT")
        
    def openStream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                         input_device_index=0,
                         channels=self.CHANNELS,
                         rate=self.RATE,
                         input=True,
                         frames_per_buffer=self.CHUNK)
        self.frames = []
        self.stopped = False
        #self.startTimer()
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
        print("recording")
        data = self.stream.read(self.CHUNK)
        self.currentAudioFrame.put(data)
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
class YinEstimator(QObject):
    def __init__(self, currentAudioFrame, currentAudioNote, parent=None, chunk = 4096, rate = 44100,
                f0_max=1000, f0_min=100, harmoThresh=0.15, medianOrder=5):
        super(YinEstimator, self).__init__(parent)
        self.stop=False
        self.quantizerInit()
        self.w_len = chunk
        self.tau_min = int(rate / f0_max)
        self.tau_max = int(rate / f0_min)
        self.harmo_thresh=harmoThresh
        self.RATE = rate
        self.currentAudioFrame = currentAudioFrame
        self.currentAudioNote = currentAudioNote
        self.pitchMedianBuffer = deque([], medianOrder)
        [self.pitchMedianBuffer.append(0) for i in range(medianOrder)]
        print("Yin Init ")
    @pyqtSlot()
    def process(self):
        print("Yin Process ")
        while not self.stop:
            # aa = time.time()
            data = self.currentAudioFrame.get(block=True)
            decodedData = np.frombuffer(data, dtype='<i2').reshape(-1, 1)
            wavData = np.asarray(decodedData, dtype=np.int16).reshape(-1, 1)
            #print("processing")
            df = self.differenceFunction(wavData.squeeze(), self.w_len, self.tau_max)
            cmdf = self.cumulativeMeanNormalizedDifferenceFunction(df, self.tau_max)
            p = self.getPitch(cmdf, self.tau_min, self.tau_max, self.harmo_thresh)
            if p != 0: # A pitch was found
                pitch = float(self.RATE / p)
                harmonic_rate = cmdf[p]
            else: 
                pitch = 0
                harmonic_rate = min(cmdf)
            self.pitchMedianBuffer.append(pitch)
            actualNote = np.median(list(self.pitchMedianBuffer))
            noteMidi, noteLabel = self.quantizePitch([actualNote], self.centroids, self.codeBookMidi, self.codeBookLabel)
            #print(f"Note = {noteLabel[0]}  Hz = {pitch}  midi = {noteMidi[0]}  ap_pwr = {harmonic_rate}")
            self.currentAudioNote.put(noteMidi[0])
    def differenceFunction(self, x, N, tau_max):
        #equation (6) in [1]    
        x = np.array(x, np.float64)
        w = x.size
        tau_max = min(tau_max, w)
        x_cumsum = np.concatenate((np.array([0.]), (x * x).cumsum()))
        size = w + tau_max
        p2 = (size // 32).bit_length()
        nice_numbers = (16, 18, 20, 24, 25, 27, 30, 32)
        size_pad = min(x * 2 ** p2 for x in nice_numbers if x * 2 ** p2 >= size)
        fc = np.fft.rfft(x, size_pad)
        conv = np.fft.irfft(fc * fc.conjugate())[:tau_max]
        return x_cumsum[w:w - tau_max:-1] + x_cumsum[w] - x_cumsum[:tau_max] - 2 * conv
    def cumulativeMeanNormalizedDifferenceFunction(self, df, N):
        # equation (8) in [1]
        cmndf = df[1:] * range(1, N) / np.cumsum(df[1:]).astype(float) #scipy method
        return np.insert(cmndf, 0, 1)
    def getPitch(self, cmdf, tau_min, tau_max, harmo_th=0.1):
        tau = tau_min
        while tau < tau_max:
            if cmdf[tau] < harmo_th:
                while tau + 1 < tau_max and cmdf[tau + 1] < cmdf[tau]:
                    tau += 1
                return tau
            tau += 1
        return 0    # if unvoiced
    def quantizerInit(self):
        notesHz = []
        noteLabels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.codeBookLabel = []
        self.codeBookMidi = []
        self.codeBookLabel.append('Rest')
        self.codeBookMidi.append(0)
        self.codeBookMidi.extend([i for i in range(24,108)])
        for octave in range(0,7):
            for note in range(12):
                notesHz.append((32.70809598967595*2**(octave+note/12)))
                self.codeBookLabel.append(noteLabels[note]+str(octave+1))
        self.centroids = []
        self.centroids.append(1)
        self.centroids.extend([(notesHz[i]+notesHz[i+1])/2 for i in range(len(notesHz)-1)])
    def quantizePitch(self, signal, partitions, codebookMidi, codebookLabel):
        indices = []
        quantaMidi = []
        quantaLabel = []
        for datum in signal:
            index = 0
            while index < len(partitions) and datum > partitions[index]:
                index += 1
            indices.append(index)
            quantaMidi.append(codebookMidi[index])
            quantaLabel.append(codebookLabel[index])
        return quantaMidi, quantaLabel
    def stopit(self):
        self.stop = True
        # self.timer.stop()
        #self.saveRecording()
class Audio2MidiEvents(QObject):
    def __init__(self, currentAudioNote, currentAudio2MidiEvent, parent = None,):
        super(Audio2MidiEvents, self).__init__(parent)
        self.currentAudioNote = currentAudioNote
        self.currentAudio2MidiEvent = currentAudio2MidiEvent
        self.stop = False
        self.lastNote = ''
    def stopit(self):
        self.stop = True
    @pyqtSlot()
    def process(self):
        while not self.stop:
            # aa = time.time()
            data = self.currentAudioNote.get(block=True)
            #print(data)
            if data != self.lastNote:
                if self.lastNote != 0:
                    pass
                    #print([144,self.lastNote, 0])
                if data >=0:
                    #print([144,data,127])
                    self.currentAudio2MidiEvent.put(['noteOn', 144, data])#,self.newNote))
                    print(['noteOn', 144, data])
                self.lastNote = data
class TryApp(QObject):
    def __init__(self , parent = None):
        super(TryApp, self).__init__(parent)
        self.currentAudioFrame = Queue()
        self.currentAudioNote = Queue()
        self.currentAudio2MidiEvent = Queue()
        self.stopTimer = QTimer(timeout=self.killAll, singleShot=True)
        self.stopTimer.start(20000)
        self.startProc()
    def startProc(self):
        self.audioRecorder = AudioRecorder(currentAudioFrame = self.currentAudioFrame, parent=self, chunk = 4*1024 )
        self.audioRecorder.stopStartRecorder('Audio Mic')
        self.threadPitchEstimator = QThread()
        self.pitchEstimator = YinEstimator(currentAudioFrame = self.currentAudioFrame, parent=None, currentAudioNote = self.currentAudioNote,  harmoThresh=0.15, medianOrder=3)
        self.pitchEstimator.moveToThread(self.threadPitchEstimator)
        self.threadAudio2MidiEvents = QThread()
        self.audio2MidiEvents = Audio2MidiEvents(currentAudioNote = self.currentAudioNote, currentAudio2MidiEvent = self.currentAudio2MidiEvent, parent=None)
        self.audio2MidiEvents.moveToThread(self.threadAudio2MidiEvents)
        self.threadPitchEstimator.start()
        self.threadAudio2MidiEvents.start()
        self.threadAudio2MidiEvents.started.connect(self.audio2MidiEvents.process)
        self.threadPitchEstimator.started.connect(self.pitchEstimator.process)
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
    #audioRecorder = AudioRecorder(currentAudioFrame = currentAudioFrame, chunk = 2048 )
    
#    threadPitchEstimator = QThread()
#    pitchEstimator = YinEstimator(currentAudioFrame = currentAudioFrame, currentAudioNote = currentAudioNote)
#    pitchEstimator.moveToThread(threadPitchEstimator)
#
#    threadAudioRecorder.start()
    #threadPitchEstimator.start()
