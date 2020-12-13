from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QLCDNumber, QDoubleSpinBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot, QThread
from utils import Params, TensorBuffer, rename, midi2Tensor
from ParsingClasses import Vocabulary
import pickle, time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import weight_norm
import torch.optim as optim 
from pathlib import Path

from Models.LstmMidiOnly import Model as ModelMidi
from Models.LstmKeyOnlySkipCond import Model as ModelKey
import json
from collections import deque

class NeuralNet(QObject):  
    def __init__(self, currentDnnNote, notesDict, appctxt, parentPlayer, parent):
        super(NeuralNet, self).__init__()
        self.appctxt = appctxt
        self.parentPlayer = parentPlayer
        self.parent = parent
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.loadVocabularies()
        self.notesDict = notesDict
        self.device = torch.device('cpu')#('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.currentDnnNote = currentDnnNote

        # tensor buffers for the 4 types of input that go in the NN. 
        # the size in the time axis is 4, but currently the NN accepts only 1 every timestep 
        self.tensorBuffer = TensorBuffer(maxLen=4, shape = [2,1], restIndex=self.restTokenIndex, device=self.device)
        self.tensorBufferPC = TensorBuffer(maxLen=4, shape = [2,1], restIndex=12, device=self.device)
        self.tensorBufferRhythm = TensorBuffer(maxLen=4, shape = [1,1], restIndex=0, device=self.device)
        self.tensorBufferKey = TensorBuffer(maxLen=4, shape = [1,1], restIndex=12, device=self.device)

        self.first = 0
        self.prevPredictionTokenIndex = self.vocabMidiArticGlobal.token2index['0_1']
        self.prevPredictionTokenIndexPC = 12
        self.prevPredictionTokenIndexKey = 12 # C major
        self.timeSignature2ticks(self.config.timeSignature)

        self.old = time.time()
        self.enforceMode = False#True
        self.voices = 2
        self.conditionFlag = False
        self.useCondition = False
        self.condition = None
        self.insideCondition = False
        self.initializeModel()
        self.info = {
            'type' : self.parentPlayer.type,
            'name' : self.parentPlayer.name,
            'midiModel': {
                'path' : self.midiModelPath,
                'args' : self.args
            },
            'keyModel' : {
                'path' : self.keyModelPath,
                'args' : self.argsKey
            }
        }
    def timeSignature2ticks(self, timeSignature):
        [nom,denom] = timeSignature.split("/")
        nom = int(nom)
        denom = int(denom)
        self.timeSignature = timeSignature
        self.dur = nom*(16//denom)
    def initializeModel(self):
        self.midiModelPath = 'Checkpoints/saved_svine_last.pt'
        self.keyModelPath = 'Checkpoints/saved_frozen_best_SkipCond1271.pt'
        loadedCheckpointMidi = torch.load(self.appctxt.get_resource(self.midiModelPath),map_location=self.device)
        argsMidi = loadedCheckpointMidi['args']
        loadedCheckpointKey = torch.load(self.appctxt.get_resource(self.keyModelPath),map_location=self.device)
        argsKey = loadedCheckpointKey['args'][0]

        self.modelMidi = ModelMidi(embSizeMidi=argsMidi.embSizeMidi, vocabSizeMidi=135, dropoutEmb=argsMidi.dropoutEmb, dropoutLstm=argsMidi.dropoutLstm, 
                    numLayersMidiLSTM=argsMidi.lstmLayers, hiddenSize=argsMidi.hiddenSize,
                    embSizePitchClass = argsMidi.embSizePitchClass, vocabSizePitchClass = 13,
                    embSizeRhythm = argsMidi.embSizeRhythm, vocabSizeRhythm = 10,  
                    concatInputs = argsMidi.concatInputs , voices = argsMidi.voices, includeRhythm = argsMidi.includeRhythm, initHiddenZeros=0)#argsMidi.initHiddenZeros)#, stackSize = 32)#args.initHiddenZeros )initHiddenZeros = 1)#
        self.modelKey = ModelKey(dropoutKey=argsKey.dropoutKey, 
                            numLayersKeyLSTM=argsKey.lstmLayersKey, hiddenSizeKey=argsKey.hiddenSizeKey,
                            vocabSizeKey = 24, embSizeKeys = 25, includeKeys = 0, initKeys = 0,
                            initHiddenZeros = 0)#argsKey.initHiddenZeros)
        self.i = 0
        self.modelMidi.to(self.device)   
        self.modelKey.to(self.device)
        self.modelMidi.eval() 
        self.modelKey.eval()
        self.modelMidi.load_state_dict(loadedCheckpointMidi['state_dict'])
        self.modelKey.load_state_dict(loadedCheckpointKey['state_dict'])
        self.temperature = self.parentPlayer.temperature # self.params['machine']["temperature"]
        self.args = argsMidi
        self.argsKey = argsKey
        self.tensorBufferHidden = deque(maxlen=16)#TensorBuffer(maxLen=16, shape = [1,args.lstmLayers * args.hiddenSize], restIndex = 0, 
                                                #device = self.device, typeTensor = 'float')
        self.hiddenListBad = []
        self.hiddenListGood = []
        self.initHiddenStates()

    @pyqtSlot(str)
    def selectModel(self, value):
        pass

    @pyqtSlot()
    def initHiddenStates(self):
        #torch.manual_seed(554)
        # if self.first == 0 :
        #     with open("hiddenGoodInitBass", 'rb') as hidGood :
        #         self.hiddenMidi = pickle.load(hidGood)
        #     self.first =1
        # else:
        self.hiddenMidi = self.modelMidi.init_hiddenMidi(1,self.device)
        self.hiddenKey = self.modelKey.init_hiddenKey(1,self.device)
        self.prevPredictionTokenIndex = self.vocabMidiArticGlobal.token2index['0_1']#self.restTokenIndex
        self.prevPredictionTokenIndexPC = 12
        self.prevPredictionTokenIndexKey = 12
        self.tensorBufferHidden.clear()
        self.firstHiddenMidi = self.hiddenMidi
        #self.stack = self.model.initStack(1,self.device)
        #self.hiddenRhythm = self.model.init_hiddenRhythm(1,self.device)
    def saveHiddenStates(self, label):
        if label==0:
            self.hiddenListBad.extend(list(self.tensorBufferHidden))
            print(len(self.hiddenListBad))
        elif label == 1:
            self.hiddenListGood.extend(list(self.tensorBufferHidden))
            # with open("hiddenGoodInitBass", 'wb') as hidGood :
            #     pickle.dump(self.firstHiddenMidi, hidGood)
        self.tensorBufferHidden.clear()
    def hidden2pickle(self):
        try:
            with open("hiddenSoprano", 'rb') as f :
                aaa = pickle.load( f)
                self.hiddenListBad.extend(aaa)
            with open("hiddenBass", 'rb') as f :
                aaa = pickle.load( f)
                self.hiddenListGood.extend(aaa)
        except Exception:
            pass
        with open("hiddenSoprano", 'wb') as hidBad :
            pickle.dump(self.hiddenListBad, hidBad)
        with open("hiddenBass", 'wb') as hidGood :
            pickle.dump(self.hiddenListGood, hidGood)
    def loadVocabularies(self):
        with open(self.appctxt.get_resource("Vocabularies/globalVocabsDictOld.voc"), "rb") as f:
            self.vocabsDict = pickle.load(f)
        self.vocabMidiArticGlobal = self.vocabsDict['midiArtic']
        self.vocabSizeMidiArtic = len(self.vocabMidiArticGlobal.token2count.keys())
        self.restTokenIndex = self.vocabMidiArticGlobal.token2index['0_1']

        self.vocabRhythmGlobal = self.vocabsDict['rhythm']
        self.vocabSizeRhythm = len(self.vocabRhythmGlobal.token2count.keys())

        self.vocabKeysGlobal = self.vocabsDict['keys']
        self.vocabSizeKeys = len(self.vocabKeysGlobal.token2count.keys())

    # @pyqtSlot()
    # def changeEnforceState(self):
    #     self.enforceMode = self.enforceMode ^ True
    
    # def changeConditionFlag(self):
    #     self.conditionFlag = self.conditionFlag ^ True
    #     if self.conditionFlag is True:
    #         self.conditionPiece = self.loadConditionFile()
    #     else:
    #         self.conditionPiece = None
    # @pyqtSlot()
    # def loadConditionFile(self):
    #     self.mode = 2
    #     if self.mode == 1:
    #         with open(self.appctxt.get_resource('condition.json'), "r") as f:
    #             self.condJson = json.load(f)
    #         self.condMidiInd = self.vocabMidiArticGlobal.token2index['0_1']
    #         self.condCpcInd = 12
    #         self.condKeyInd = 12
    #         self.condStart = 0
    #         self.condEnd = 15
    #         self.condDur = 16
    #         self.condWhere = 0
    #         self.useCondition = True
    #     else:
    #         # with open(self.appctxt.get_resource('twinkleForVide.mid'), "r") as f:
    #         #     self.condJson = picle.load(f)
    #         self.condJson =  midi2Tensor(self.appctxt.get_resource('cond1.mid'), self.vocabMidiArticGlobal, self.vocabRhythmGlobal)

    #         self.condMidiInd = self.vocabMidiArticGlobal.token2index['0_1']
    #         self.condCpcInd = 12
    #         self.condKeyInd = 12
    #         self.condStart = 0
    #         self.condEnd = self.condJson[1].shape[0] - 1
    #         self.condDur = self.condEnd + 1
    #         self.condWhere = 0
    #         self.useCondition = True
    #     #print(self.useCondition)
        

    @pyqtSlot(dict) # signal apo midiKeyboardReadSync
    def forwardPass(self, currentKeyNote):
        ee = time.time()
        #print(f"JUST ENTERD NEURAL NET for tick {currentKeyNote['tick']} at time {time.time()}")
        with torch.no_grad():
            ################## RECEIVE Note From MidiKeyboardReadSync and convert It
            #print(currentKeyNote)
            [currentKeyMidi, currentKeyHit, currentKeyTick, currentRhythmToken] = [currentKeyNote['midi'], currentKeyNote['artic'], currentKeyNote['tick'], currentKeyNote['rhythmToken']]
            currentRhythmInd = self.vocabRhythmGlobal.token2index[currentRhythmToken]
            #self.tensorBufferRhythm.push([currentRhythmInd])

            if currentKeyMidi != 0:
                #note = pitch.Pitch(midi = int(currentKeyMidi))
                #pitchClassName = note.name
                #fullName = note.nameWithOctave
                print(f"midi is {currentKeyMidi} and type is {currentKeyMidi.__class__}")
                currentKeyPitchClassIndex = int(self.notesDict[currentKeyMidi]['primary']['cpc'])
                #currentKeyPitchClassIndex = note.pitchClass
            else:
                #pitchClassName = 'Rest'
                #fullName = 'Rest'
                currentKeyPitchClassIndex = 12

            if currentKeyTick == self.dur - 1:
                currentKeyTick = -1 # this is ugly, fix it
            currentKeyToken = str(currentKeyMidi)+"_"+str(currentKeyHit)
            try:
                currentKeyTokenInd = self.vocabMidiArticGlobal.token2index[currentKeyToken]
            except:
                # δεν παιζει, απλα μη σπασει ο διαολος το ποδαρι του
                # note Out of Vocabulary
                currentKeyTokenInd = self.restTokenIndex
            #### fill the newNextElement and push it to the TensorBuffer
            # I want to enable useCondition only when its time.
            ###
            #assert prevPredictionTokenIndex[2]
            self.tensorBuffer.push([self.prevPredictionTokenIndex,currentKeyTokenInd])
            self.tensorBufferPC.push([self.prevPredictionTokenIndexPC, currentKeyPitchClassIndex])
            self.tensorBufferKey.push([self.prevPredictionTokenIndexKey])
            #print(f" {self.prevPredictionTokenIndex.shape}")
            #print(f" {torch.cat((self.hiddenMidi[0][0,0,:],self.hiddenMidi[0][1,0,:]),dim=0).unsqueeze(0).shape}")
            #print(f"{srsrvrs}")
            #print(f"shape of slice {self.hiddenMidi[0][0,:,:].shape} shape of hiddenMidi {self.hiddenMidi[0].shape}")# shape of cat {torch.cat((self.hiddenMidi[0,:,:],self.hiddenMidi[1,:,:]),dim=1)}")
            self.tensorBufferHidden.append(torch.cat((self.hiddenMidi[0][0,0,:],self.hiddenMidi[0][1,0,:]),dim=0).cpu().numpy())
            #self.tensorBufferHidden.push([torch.cat((self.hiddenMidi[0][0,0,:],self.hiddenMidi[0][1,0,:]),dim=0).unsqueeze(0)])
            # self.tensorBuffer.push([96,96])
            # self.tensorBufferPC.push([12,12])
            #####################
            # I need a tensorBuffer for Rhythm, and for PitchClass
            # midi size = pitchClass size = batch x voices x window
            # rhythm size = batch x 1 x window
            # size of tensorBuffer is self.voices,1,self.maxLen

            midi = self.tensorBuffer.data[0:self.voices,0,-1].view(1,-1,1)
            pitchClass = self.tensorBufferPC.data[0:self.voices,0,-1].view(1,-1,1)
            #rhythm =  self.tensorBufferRhythm.data[:,0,:].view(1,-1,1)
            rhythm = torch.tensor([currentRhythmInd]).view(1,-1,1).to(self.device)
            key = self.tensorBufferKey.data[0:1,0,-1].view(1,-1,1)
            # midi = self.tensorBuffer.data[0:self.voices,0,:].view(1,-1,32)
            # pitchClass = self.tensorBufferPC.data[0:self.voices,0,:].view(1,-1,32)
            # rhythm =  self.tensorBufferRhythm.data[:,0,:].view(1,-1,32)
            # #rhythm = torch.tensor([currentRhythmInd]).view(1,-1,1).to(self.device)

            #print(f"currentTick = {currentKeyTick} with token {currentRhythmToken}")
            #print(f"input {midi} while the total buffer is {self.tensorBuffer.data[0:self.voices,0,:]}")
            ###print(self.tensorBuffer.data)
            # midi shape 16,2,128 /// rhythm shape 16,1,128
            ###print(midi.shape)
            ###print(rhythm.shape)
            #predictedLogits, outSoftmax, predictedLogSoftmax, self.hiddenMidi, self.hiddenRhythm,_ = self.model(midi, pitchClass, rhythm, 1 ,hiddenMidi=self.hiddenMidi,device = self.device)#, stack = self.stack) #, 
            #predictedLogits, outSoftmax, predictedLogSoftmax,self.hiddenMidi,self.hiddenRhythm,_,keyLogits,_,_ = self.model(midi, pitchClass, rhythm, key, 1, hiddenMidi=self.hiddenMidi, device = self.device)#, means = means, std = 1)
            
            outputMidi = self.modelMidi(midi, pitchClass, rhythm, currentBatchSize = 1, hiddenMidi = self.hiddenMidi, device = self.device)
            #print(outputMidi.keys())
            predictedLogits = outputMidi['midi']['logits']
            midiLogits = outputMidi['midi']['midiBeforeFc']
            #midiLogits = midiLogits.detach()
            self.hiddenMidi = outputMidi['hiddenOut']['midi']

            outputKey = self.modelKey( key, midiLogits,1, hiddenKey = self.hiddenKey, device = self.device)
            self.hiddenKey = outputKey['hiddenOut']['key']
            predictedKeyLogits = outputKey['key']['logits']  

            #predictedLogSoftmax, predictedLogits = self.model(self.tensorBuffer.data.permute(1,0,2))
            output_dist = nn.functional.softmax( predictedLogits.div(self.parentPlayer.temperature),dim=1 ).data
            output_dist_key = nn.functional.softmax( predictedKeyLogits.div(0.2),dim=1 ).data
            #######output_distKey = nn.functional.softmax( keyLogits.div(0.1),dim=1 ).data
            #######predictedKey = torch.multinomial(output_distKey, 2, replacement=True)
            #print(output_dist.shape.numel())
            #print(output_dist[output_dist<=0].shape.numel())
            predictedData = torch.multinomial(output_dist, 2, replacement=True)
            predictedKey = torch.multinomial(output_dist_key, 2, replacement=True)
            #print(predictedData)
            #if predictedData[0][0].item() == self.restTokenIndex:
            #    predictedData[0][0]=predictedData[0][1]
            self.prevPredictionTokenIndex = predictedData[0][0].item()
            self.prevPredictionTokenIndexKey = predictedKey[0][0].item()
            #######self.prevPredictionTokenIndexKey = predictedKey[0][0].item()
            #######print("************************************************************************\n")
            #######print(f"{self.vocabKeysGlobal.index2token[self.prevPredictionTokenIndexKey]}")
            #print(f"output {self.prevPredictionTokenIndex}")
            # find  pitch class of prediction
            [predictedMidi,predictedHit] = self.vocabMidiArticGlobal.index2token[self.prevPredictionTokenIndex].split("_")

            #print("****************************************************************")
            #print(f"*******************{self.vocabKeysGlobal.index2token[self.prevPredictionTokenIndexKey]}******************************************")
            #self.prevPredictionTokenIndexPC = pitch.Pitch(midi = int(predictedMidi)).pitchClass
            self.parent.toolbar.keyIndicator.setText(self.vocabKeysGlobal.index2token[self.prevPredictionTokenIndexKey])
            self.prevPredictionTokenIndexPC =  int(self.notesDict[int(predictedMidi)]['primary']['cpc'])
            
            
            ############# Convert Predicted Bach to Midi,Hit,Tick
            """ a = torch.FloatTensor(200,512).fill_(1)
            for i in range(1000):
                a = a*a
            if currentKeyMidi == 0: # rest
                #send rest
                ee = currentKeyMidi
                currentKeyHit = 1
            else:
                ee = currentKeyMidi + ((-1)**random.randrange(-2,2)) * ( currentKeyMidi * (random.randrange(0,20)*0.01)) """
            #self.i += 1
            #print(f"NEURAL NET PREDICTED {self.i} at tick {currentKeyTick} for tick {currentKeyTick+1}")
            output = {
                "playerName" :self.parentPlayer.name, 
                "keyEstimation" : self.vocabKeysGlobal.index2token[self.prevPredictionTokenIndexKey],
                "midi" : int(predictedMidi),
                "artic":  int(predictedHit),
                "tick": currentKeyTick+1,
                "rhythmToken": None
            }
            self.currentDnnNote.put(output)
        #print(f"TIME ELAPSED for NN is {time.time()-ee}")
class NeuralNetSync(QObject):
    neuralNetSyncOutputSignal = pyqtSignal(dict)
    def __init__(self, currentDnnNote, parentPlayer):
        super(NeuralNetSync,self).__init__()
        self.currentDnnNote = currentDnnNote
        self.parentPlayer = parentPlayer

    @pyqtSlot(dict) # signal from clock
    def getNewNeuralNetPrediction(self, clockTriger):
        tick = clockTriger['tick']
        rhythmToken = clockTriger['rhythmToken']
        globalTick = clockTriger['globalTick']
        try:
            output = {}
            while not self.currentDnnNote.empty():
                output = self.currentDnnNote.get(block = False)
            #print(self.currentDnnNote.empty())
            output['rhythmToken'] = rhythmToken
            output['globalTick'] = globalTick
            # print(f"NN Sync emits signal to manager BEFPRE {result} and ID {self.parentPlayer.name}")
            # result[tick].append(rhythmToken)
            # print(f"NN Sync emits signal to manager {result[tick]} and ID {self.parentPlayer.name}")
            # output = {
            #     "playerName" : self.parentPlayer.name, 
            #     "keyEstimation" : None,
            #     "midi" : None,
            #     "artic": 0,
            #     "tick": 0,
            #     "rhythmToken": None
            # }
            self.neuralNetSyncOutputSignal.emit(output)
            #print(f"DNN SYNC EMITed {output}  , at tick {tick} at time {time.time()}")
        except Exception as e:
            print(f"SLOW DOWN COWBOY {e}")
            output = {
                    "playerName" :self.parentPlayer.name, 
                    "keyEstimation" : "None",
                    "midi" : 0,
                    "artic":  1,
                    "tick": tick,
                    "globalTick" : globalTick,
                    "rhythmToken": rhythmToken
                }
            self.neuralNetSyncOutputSignal.emit(output)
            print(f"DNN SYNC EMITed {output}  , at tick {tick} at time {time.time()}")