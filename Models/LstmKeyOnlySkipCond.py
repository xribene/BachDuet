import torch
import torch.nn as nn

class Model(torch.nn.Module):
    def __init__(self,  dropoutKey=0.2, 
                        numLayersKeyLSTM=2, hiddenSizeKey=100,
                        vocabSizeKey = 24, embSizeKeys = 25, includeKeys = 0, initKeys = 0,
                        initHiddenZeros = 1
                        ):
        super(Model, self).__init__()
        ######### MIDI parameters
        self.embSizeKeys = embSizeKeys
        self.vocabSizeKey = vocabSizeKey
        self.hiddenSizeKey = hiddenSizeKey
        self.outputKeySize = vocabSizeKey
        self.numLayersKeyLSTM = numLayersKeyLSTM
        self.initHiddenZeros = initHiddenZeros
        ###################################
        self.embKeys = nn.Embedding(self.vocabSizeKey, self.embSizeKeys)
        self.fcKeys = nn.Linear(self.hiddenSizeKey,self.outputKeySize)
        self.dropout = nn.Dropout(p=dropoutKey)
        self.lstmKeys = nn.LSTM(self.embSizeKeys + self.hiddenSizeKey, self.hiddenSizeKey, self.numLayersKeyLSTM,
                                        batch_first=True)
        
        self.fcCond = nn.Linear(600, self.hiddenSizeKey)
        self.fcCond2 = nn.Linear(600, self.hiddenSizeKey)
        self.fcKeys = nn.Linear(self.hiddenSizeKey , self.outputKeySize)
        self.softmax = nn.Softmax(dim=1)
        self.logSoftmax = nn.LogSoftmax(dim=1)
        ###################################
        self.initParams()
        
    def init_hiddenKey(self, currentBatchSize,device):
        hc = (torch.FloatTensor(self.numLayersKeyLSTM, currentBatchSize, self.hiddenSizeKey).normal_().to(device),
                torch.FloatTensor(self.numLayersKeyLSTM, currentBatchSize, self.hiddenSizeKey).normal_().to(device) )
        return hc
    def repackage_hidden(self, hidden):
        if isinstance(hidden, torch.Tensor):
            return hidden.detach()
        else:
            return tuple(self.repackage_hidden(v) for v in hidden)
    def initParams(self):
        for param in self.parameters():
             if len(param.shape)>1:
                 torch.nn.init.xavier_normal_(param)
    def forward(self, key, lstmOutMidi, currentBatchSize,device, hiddenKey = None, 
                            currentDropout = None):
        if currentDropout is not None:
            self.dropoutEmb.p = currentDropout
            self.dropoutLstm.p = currentDropout
        if hiddenKey is None:
            hiddenKey = self.init_hiddenKey(currentBatchSize,device)
        else:
            hiddenKey = self.repackage_hidden(hiddenKey)

        keyEmb = self.embKeys(key)
        # First for midi LSTM 
        keyEmb = self.dropout(keyEmb) #+ pitchClassEmb / batch x window  x features
        # 8 x 1 x seqLen x embSize
        condForCat = self.fcCond(self.dropout(lstmOutMidi)).view(keyEmb.shape[0], keyEmb.shape[2], -1)
        aaa = torch.cat((keyEmb[:,0,:,:],condForCat), dim=2)
        lstmOutKey, hiddenOutKey = self.lstmKeys(aaa, hiddenKey)
        #lstmOutMidiDense = lstmOutMidi.contiguous().view(-1,lstmOutMidi.shape[2]) # batchXwindow x 600
        #lstmOutMidiDense = self.dropout(lstmOutMidiDense)
        lstmOutKey = lstmOutKey + self.fcCond2(self.dropout(lstmOutMidi)).view(keyEmb.shape[0], keyEmb.shape[2], -1)
        #lstmOutKeyForCat = lstmOutKey.contiguous().view(-1,lstmOutKey.shape[2]) # batchXwindow x 600
        lstmOutKey = lstmOutKey.contiguous().view(-1,lstmOutKey.shape[2]) # batchXwindow x 600
        #forFcKeys = torch.cat((condForCat, lstmOutKeyForCat),dim=1)
        keyLogits = self.fcKeys(lstmOutKey)
        
        keySoftmax = self.softmax(keyLogits) #if self.includeKeys else None
        keyLogSoftmax = self.logSoftmax(keyLogits) #if self.includeKeys else None

        output = {
            'key':{
                'logits':keyLogits,
                'softmax':keySoftmax,
                'logSoftmax':keyLogSoftmax
            },
            'hiddenOut':{
                'key':hiddenOutKey
            }
        }
        return output