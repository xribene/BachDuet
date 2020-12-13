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
import scipy.io.wavfile
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import time

class AudioRecorder(QObject):
    def __init__(self, parent=None ):
        super(AudioRecorder, self).__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.paparia)
        self.timer.start(200)
        #self.timer  = QTimer.singleShot(200, self.paparia)
    def paparia(self):
        print('paparia')
        a = 4
        b = a+4
        return b
    def stopit(self):
        self.timer.stop()
        print("stop recording")
class TryApp(QWidget):
    def __init__(self , parent = None):
        super(TryApp, self).__init__(parent)
        self.stopTimer = QTimer(timeout=self.killAll, singleShot=True)
        self.stopTimer.start(4000)
        self.startProc()
    def startProc(self):
        self.audioRecorder = AudioRecorder(self)
        #time.sleep(4)
        #self.killAll()
    def killAll(self):
        print("KKKKKIIIIIIIIIIIIILLLLLLLLLLLLLLLLLLLLLLLLLL")
        self.audioRecorder.stopit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = TryApp()
    #audioRecorder = AudioRecorder()
    
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
