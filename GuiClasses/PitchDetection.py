# -*- coding: utf-8 -*-
"""
Created on Sun May 19 05:08:43 2019

@author: xribene
"""

# import pyaudio
import wave
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
# import scipy.io.wavfile
# import scipy.io
from Yin.yin import differenceFunction,cumulativeMeanNormalizedDifferenceFunction,getPitch
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class YinEstimator(QObject):
    def __init__(self, currentAudioFrame, currentAudioNote, parent=None chunk = 2048, rate = 44100,
                f0_max=1000, f0_min=100, harmoThresh=0.1, medianOrder=7
                ):
        super(YinEstimator, self).__init__(parent)
        self.stop=False
        self.quantizerInit()
        self.w_len = chunk
        self.tau_min = int(rate / f0_max)
        self.tau_max = int(rate / f0_min)
        self.harmo_thresh=harmoThresh
        # self.timer = QTimer()
        # self.timer.start(1)
        # self.timer.timeout.connect(self.record)
        self.currentAudioFrame = currentAudioFrame
        self.currentAudioNote = currentAudioNote
        self.pitchMedianBuffer = deque([], medianOrder)
        self.process()
    def process(self):
        while not self.stop:
            segment = self.currentAudioFrame.get(block=True)
            df = differenceFunction(segment.squeeze(), self.w_len, self.tau_max)
            cmdf = cumulativeMeanNormalizedDifferenceFunction(df, self.tau_max)
            p = getPitch(cmdf, self.tau_min, self.tau_max, self.harmo_thresh)
            if np.argmin(cmdf)>self.tau_min:
                argmin = float(self.RATE / np.argmin(cmdf))
            if p != 0: # A pitch was found
                pitch = float(self.RATE / p)
                harmonic_rate = cmdf[p]
            else: # No pitch, but we compute a value of the harmonic rate
                harmonic_rates = min(cmdf)
                pitch = 0
            _, note = self.quantizePitch([pitch], self.centroids, self.codeBook)
            self.pitchMedianBuffer.append(note[0])
            actualNote = np.median(self.pitchMedianBuffer)
            self.currentAudioNote.put(actualNote)
    def quantizerInit(self):
        notesHz = []
        noteLabels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.codeBook = []
        self.codeBook.append('Rest')
        for octave in range(0,7):
            for note in range(12):
                notesHz.append((32.70809598967595*2**(octave+note/12)))
                self.codeBook.append(noteLabels[note]+str(octave+1))
        self.centroids = []
        self.centroids.append(1)
        self.centroids.extend([(notesHz[i]+notesHz[i+1])/2 for i in range(len(notesHz)-1)])
    def quantizePitch(self, signal, partitions, codebook):
        indices = []
        quanta = []
        for datum in signal:
            index = 0
            while index < len(partitions) and datum > partitions[index]:
                index += 1
            indices.append(index)
            quanta.append(codebook[index])
        return indices, quanta
    def stopit(self):
        self.stop = True
        # self.timer.stop()
        #self.saveRecording()

if __name__ == '__main__':
    recorder = AudioRecorder()
    music = recorder.record()
    scipy.io.wavfile.write('scipy.wav',44100,music)
    recorder.stopRecording()
    recorder.saveRecording()

