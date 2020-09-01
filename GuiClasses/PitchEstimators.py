import pyaudio
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
import numpy as np
import time
from queue import Queue
from collections import deque
import sys
import pickle, time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import weight_norm
import torch.optim as optim 
from pathlib import Path
import json

class Crepe(nn.Module):
    def __init__(self, modelSize, appctxt):
        super(Crepe, self).__init__()
        self.appctxt = appctxt
        with open(self.appctxt.get_resource(f'Checkpoints/Crepe/modelCheckpoint{modelSize}.pk'), 'rb') as handle:
            self.checkpoint = pickle.load(handle)
        self.arc = json.loads(self.checkpoint['json'])
        # I expect the input shape to be N,Cin,Lin --> N,1,1024
        # Normally I wouldn't need this info, but I need it to do
        # a manual assymetric zero padding before each Conv layer
        # in order to imitate tensorflow's "same" padding technique
        inputShape = (None,1,1024)
        self.layers = nn.ModuleList()
        self.convCounter = 0
        layers = self.arc['config']['layers']
        modelInd = self.arc['config']['name'].replace('model','')
        channelOut = inputShape[1]
        currentOutShape = inputShape
        data_type = torch.float32
        for layer in layers:
            layerProps = layer['config']
            if 'Conv' in layer['class_name']:
                self.convCounter += 1
                # it works only for 1d conv for now. 
                currentInpShape = currentOutShape
                channelIn = channelOut
                channelOut =layerProps['filters']
                kernel = layerProps['kernel_size'][0]
                stride = layerProps['strides'][0]
                if layerProps['padding'] == 'same':
                    currentOutShape = (None, channelOut, currentInpShape[2]//stride)
                    # From tensorflow documentation, about padding
                    # Total padding on rows and cols is
                    # Pr = (R' - 1) * S + (Kr - 1) * Dr + 1 - R
                    # Pc = (C' - 1) * S + (Kc - 1) * Dc + 1 - C
                    # where (R', C') are output dimensions, (R, C) are input dimensions, S
                    # is stride, (Dr, Dc) are dilations, (Kr, Kc) are filter dimensions.
                    # We pad Pr/2 on the left and Pr - Pr/2 on the right, Pc/2 on the top
                    # and Pc - Pc/2 on the bottom.  When Pr or Pc is odd, this means
                    # we pad more on the right and bottom than on the top and left.
                    C_p = currentOutShape[2]
                    C = currentInpShape[2]
                    S = stride
                    Kc = kernel
                    Dc = 1
                    Pc = (C_p - 1) * S + ( Kc - 1) * Dc + 1 - C
                    right = Pc - Pc//2
                    left = Pc//2
                    self.layers.append(nn.ZeroPad2d((left,right,0,0)))
                self.layers.append(nn.Conv1d(channelIn, channelOut, kernel, 
                                                stride, padding=0, bias=True))
                # get the weights from the loaded checkpoint
                keys = [f"{layerProps['name']}{modelInd}/kernel:0", 
                        f"{layerProps['name']}{modelInd}/bias:0"]
                weight = torch.tensor(self.checkpoint[keys[0]]).float()
                # tf/kers conv2d weights have shape (kernelx, kernely, channelIn, channelOut)
                weight = torch.squeeze(weight, dim=1).permute(2,1,0)
                bias = torch.tensor(self.checkpoint[keys[1]]).float()
                # bias = torch.zeros(self.checkpoint[keys[1]].shape).float()
                self.layers[-1].weight.data = weight
                self.layers[-1].bias.data = bias
                if layerProps['activation'] == 'relu':
                    self.layers.append(nn.ReLU())
                elif layerProps['activation'] == 'sigmoid':
                    self.layers.append(nn.Sigmoid())
                else:
                    raise Exception
            if 'MaxPool' in layer['class_name']:
                kernel = layerProps['pool_size'][0]
                stride = layerProps['strides'][0]
                # from pytorch doc
                # outShape = (Lin + 2*padding - dilation(kernel-1) -1 )/stride + 1
                # for crepe I know that padding = 0, dilation = 1, stride = kernel
                currentOutShape = (None, currentOutShape[1], (currentOutShape[2]-(kernel-1)-1)//stride+1)
                self.layers.append(nn.MaxPool1d(kernel_size=kernel, stride = stride))
            if 'BatchNormalization' in layer['class_name']:
                self.layers.append(nn.BatchNorm1d(currentOutShape[1], eps=0.0,
                            momentum=0.0))
                # in pytorc weight is gamma
                # bias is beta
                # moving_mean is running_mean
                # moving_variance is running_var

                keys = [f"{layerProps['name']}{modelInd}/gamma:0", 
                        f"{layerProps['name']}{modelInd}/beta:0", 
                        f"{layerProps['name']}{modelInd}/moving_mean:0", 
                        f"{layerProps['name']}{modelInd}/moving_variance:0" ]
                weight = torch.tensor(self.checkpoint[keys[0]]).float()
                bias = torch.tensor(self.checkpoint[keys[1]]).float()
                running_mean = torch.tensor(self.checkpoint[keys[2]]).float()
                running_var = torch.tensor(self.checkpoint[keys[3]]).float()
                # tf/kers conv2d weights have shape (kernelx, kernely, channelIn, channelOut)
                # weight = torch.squeeze(weight, dim=1).permute(2,1,0)
                # bias = torch.tensor(self.checkpoint[keys[1]]).float()
                self.layers[-1].weight.data = weight
                self.layers[-1].bias.data = bias
                self.layers[-1].running_mean.data = running_mean
                self.layers[-1].running_var.data = running_var
                pass
            if 'Dropout' in layer['class_name']:
                self.layers.append(nn.Dropout(p=layerProps['rate']))
                # pass
            if 'Dense' in layer['class_name']:
                currentInpShape = currentOutShape
                inFeature = currentInpShape[1]*currentInpShape[2]
                outFeature = layerProps['units']
                # currentOutShape = (currentInpShape)
                self.layers.append(nn.Linear(inFeature,outFeature))
                try:
                    keys = [f"{layerProps['name']}/kernel:0", 
                            f"{layerProps['name']}/bias:0" ]
                    weight = torch.tensor(self.checkpoint[keys[0]]).permute(1,0).float()
                    bias = torch.tensor(self.checkpoint[keys[1]]).float()
                except:
                    keys = [f"{layerProps['name']}_2/kernel:0", 
                            f"{layerProps['name']}_2/bias:0" ]
                    weight = torch.tensor(self.checkpoint[keys[0]]).permute(1,0).float()
                    bias = torch.tensor(self.checkpoint[keys[1]]).float()
                self.layers[-1].weight.data = weight
                self.layers[-1].bias.data = bias
                if layerProps['activation'] == 'relu':
                    self.layers.append(nn.ReLU())
                elif layerProps['activation'] == 'sigmoid':
                    self.layers.append(nn.Sigmoid())
                else:
                    raise Exception
                pass
            
    def forward(self,x):
        # out1 = self.layers[0](x)
        # out1mx = self.layers[2](out1)
        # out2 = self.layers[4](out1mx)
        # out2mx = self.layers[6](out2)
        for layer in self.layers:#[0:11]:
            if layer.__class__.__name__ == 'Linear':
                x = x.permute(0,2,1).contiguous().view(-1,layer.in_features) # .view(-1,256) #
            if layer.__class__.__name__ not in []:
                x = layer(x)
                # print(layer.__class__.__name__)
        return x
        
class CrepeEstimator(QObject):
    pitchEstimatorSignal = pyqtSignal(int)
    def __init__(self, audioFramesQueue, pitchEstimationsQueue, parentPlayer, appctxt,
                            chunk = 1024, rate = 16000, medianOrder = 1):
        super(CrepeEstimator, self).__init__()
        self.crepeModel = Crepe('Tiny', appctxt)
        self.crepeModel.eval()
        self.pitchMedianBuffer = deque([], medianOrder)
        self.quantizerInit()
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
    def to_local_average_cents(self, salience, center=None):
        """
        find the weighted average cents near the argmax bin
        """
        salience = salience.squeeze(0).detach().numpy()
        print(f"salience is {salience.shape}")
        # if not hasattr(self.to_local_average_cents, 'cents_mapping'):
        #     # the bin number-to-cents mapping
        #     self.to_local_average_cents.mapping = (
        #             np.linspace(0, 7180, 360) + 1997.3794084376191)
        mapping = np.linspace(0, 7180, 360) + 1997.3794084376191
        if salience.ndim == 1:
            if center is None:
                center = int(np.argmax(salience))
            start = max(0, center - 4)
            end = min(len(salience), center + 5)
            salience = salience[start:end]
            product_sum = np.sum(
                salience * mapping[start:end])
            weight_sum = np.sum(salience)
            return product_sum / weight_sum
        # if salience.ndim == 2:
        #     return np.array([self.to_local_average_cents(salience[i, :]) for i in
        #                     range(salience.shape[0])])
        # return None

    # raise Exception("label should be either 1d or 2d ndarray")
    @pyqtSlot(bytes)
    def process(self, data):
        # print("Crepe Process ")
        
        wavData = np.frombuffer(data, dtype=np.float32).reshape(1,-1)
        print(f"wavData {wavData.shape}, {wavData.dtype}, {np.max(wavData)}")
        # wavData = np.asarray(decodedData, dtype=np.int16).reshape(1,-1)
        # print(f"wavData {wavData.shape}, {wavData.dtype}, {np.max(wavData)}")
        # how about this ? decoded = numpy.fromstring(data, 'Float32');
        # inp = np.random.rand(1,1024)
        # aa = time.time()
        inp = torch.tensor(wavData).unsqueeze(0).float()
        salience = self.crepeModel(inp)
        # outTorch = torch.randn(1,360)
        cent = self.to_local_average_cents(salience)
        # print( f" crepe out shape is {outTorch.shape}")
        confidence, index = torch.max(salience, dim=1)
        print(f"index is {index} confidence is {confidence}")
        frequency = 10 * 2 ** (cent / 1200)
        
        noteMidi, noteLabel = self.quantizePitch([frequency], self.centroids, self.codeBookMidi, self.codeBookLabel)

        print(f"CREPE RESULT IS {cent} {frequency} {noteMidi}")
        if frequency > 1700:
            noteMidi = [0]
        self.pitchMedianBuffer.append(noteMidi[0])
        # median filtering to filter out noisy estimations
        actualNote = np.median(list(self.pitchMedianBuffer))
        # frequency[np.isnan(frequency)] = 0
        # print(f'input to Crepe Shape is {time.time()-aa}')
        self.pitchEstimatorSignal.emit(actualNote)

class YinEstimator(QObject):
    pitchEstimatorSignal = pyqtSignal(int)
    def __init__(self, audioFramesQueue, pitchEstimationsQueue, parentPlayer,  appctxt, chunk = 4096, rate = 44100,
                f0_max=1000, f0_min=100, harmoThresh=0.15, medianOrder=3):
        super(YinEstimator, self).__init__()
        self.stop=False
        self.parentPlayer = parentPlayer
        self.quantizerInit()
        self.w_len = chunk
        self.tau_min = int(rate / f0_max)
        self.tau_max = int(rate / f0_min)
        self.harmo_thresh=harmoThresh
        self.RATE = rate
        self.audioFramesQueue = audioFramesQueue # from here it reads the last audio frame of the AudioRecorder()
        self.pitchEstimationsQueue = pitchEstimationsQueue # here it pushes the pitch estimations
        self.pitchMedianBuffer = deque([], medianOrder)
        [self.pitchMedianBuffer.append(0) for i in range(medianOrder)]
        print("Yin Init ")
    @pyqtSlot(bytes)
    def process(self, data):
        # print("Yin Process ")
        # while not self.stop:
        aa = time.time()
        # data = self.audioFramesQueue.get(block=True) # block = True
        wavData = np.frombuffer(data, dtype=np.float32).reshape(-1, 1)
        # wavData = np.asarray(wavData, dtype=np.int16).reshape(-1, 1)
        #print("processing")
        df = self.differenceFunction(wavData.squeeze(), self.w_len, self.tau_max)
        cmdf = self.cumulativeMeanNormalizedDifferenceFunction(df, self.tau_max)
        # getPitch() returns 0 if there is no pitch (unvoiced sound)
        p = self.getPitch(cmdf, self.tau_min, self.tau_max, self.harmo_thresh)
        if p != 0: # A pitch was found
            pitch = float(self.RATE / p)
            harmonic_rate = cmdf[p]
        else: 
            # Rest detected
            pitch = 0
            harmonic_rate = min(cmdf)
        self.pitchMedianBuffer.append(pitch)
        # median filtering to filter out noisy estimations
        actualNote = np.median(list(self.pitchMedianBuffer))
        # I.e noteMidi = 60, noteLabel = 'C' (noteLabel spelling may be wrong, I don't use it anywhere for now)
        noteMidi, noteLabel = self.quantizePitch([actualNote], self.centroids, self.codeBookMidi, self.codeBookLabel)
        # print(f"Note = {noteLabel[0]}  Hz = {pitch}  midi = {noteMidi[0]}  ap_pwr = {harmonic_rate}")
        print(f"YIN duration is {time.time()-aa}")
        self.pitchEstimatorSignal.emit(noteMidi[0])
        # self.pitchEstimationsQueue.put(noteMidi[0])
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