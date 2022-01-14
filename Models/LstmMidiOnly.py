import torch
import torch.nn as nn

class Model(torch.nn.Module):
    def __init__(self,  embSizeMidi=125, vocabSizeMidi=135, dropoutEmb=0.2, dropoutLstm=0.4, 
                        numLayersMidiLSTM=2, hiddenSize=300,
                        embSizePitchClass = 125, vocabSizePitchClass = 13,
                        embSizeRhythm = 50, vocabSizeRhythm = 10,  
                        concatInputs = 1 , voices = 1, includeRhythm = 1, includePitchClass = 1, includeMidi = 1, initHiddenZeros = 0):
        super(Model, self).__init__()
        ######### MIDI parameters
        if not concatInputs: 
            assert embSizeMidi == embSizePitchClass
        self.vocabSizeMidi = vocabSizeMidi
        self.vocabSizePitchClass = vocabSizePitchClass
        self.vocabSizeRhythm = vocabSizeRhythm
        self.embSizeMidi = embSizeMidi #config.dict['embeddingSize']
        self.inputSizeLSTM =  voices*(embSizeMidi*includeMidi + embSizePitchClass*includePitchClass*concatInputs) + includeRhythm*embSizeRhythm
        self.hiddenSize = hiddenSize
        self.outputSize = self.vocabSizeMidi #config.dict['outputSize']
        self.embSizePitchClass = embSizePitchClass
        self.embSizeRhythm = embSizeRhythm
        #self.midiVocabSize = config.dict['midiVocabSize']
        #self.cpcVocabSize = config.dict['cpcVocabSize']
        self.numLayersMidiLSTM = numLayersMidiLSTM
        self.concatInputs = concatInputs
        self.voices = voices
        self.includeRhythm = includeRhythm 
        self.initHiddenZeros = initHiddenZeros
        ###################################
        #define layers
        ###################################
        self.embMidi = nn.Embedding(self.vocabSizeMidi, self.embSizeMidi)
        self.embPitchClass = nn.Embedding(self.vocabSizePitchClass, self.embSizePitchClass )
        self.embRhythm = nn.Embedding(self.vocabSizeRhythm, self.embSizeRhythm)
        # LSTM layers for midi+pitchClass
        #self.LstmMidi1 = nn.LSTMCell(input_size=self.inputSizeMidiLSTM, hidden_size=self.hiddenSizeMidi)
        
        # second layer lstm cell
        #self.LstmMidi2 = nn.LSTMCell(input_size=self.hiddenSizeMidi, hidden_size=self.hiddenSizeMidi) 
        
        # dropout layer for the output of the second layer cell
        self.dropoutEmb = nn.Dropout(p=dropoutEmb)
        self.dropoutLstm = nn.Dropout(p=dropoutLstm)
        # self.LstmMidi = nn.LSTM(self.inputSizeMidiLSTM,self.hiddenSizeMidi,self.numLayersMidiLSTM,batch_first=True,
        #                     dropout = self.dropout)
        # LSTM layers for rhythm summarizer
        self.LstmMidi = nn.LSTM(self.inputSizeLSTM, self.hiddenSize, self.numLayersMidiLSTM,
                                    batch_first=True)
        # Dense layers
        self.fc1 = nn.Linear(self.hiddenSize,self.outputSize)
        self.softmax = nn.Softmax(dim=1)
        self.logSoftmax = nn.LogSoftmax(dim=1)
        ###################################
        self.initParams()
        
    def init_hiddenMidi(self, currentBatchSize,device):
        #hc = (torch.FloatTensor( currentBatchSize, self.hiddenSizeMidi).normal_().to(device),
        #        torch.FloatTensor( currentBatchSize, self.hiddenSizeMidi).normal_().to(device) )
        if not self.initHiddenZeros:
            hc = (torch.FloatTensor(self.numLayersMidiLSTM, currentBatchSize, self.hiddenSize).normal_().to(device),
                    torch.FloatTensor(self.numLayersMidiLSTM, currentBatchSize, self.hiddenSize).normal_().to(device) )
        else:
            hc = (torch.zeros(self.numLayersMidiLSTM, currentBatchSize, self.hiddenSize).to(device),
                torch.zeros(self.numLayersMidiLSTM, currentBatchSize, self.hiddenSize).to(device) )
        #self.lastHidden = hc
        return hc
    def init_hiddenRhythm(self, currentBatchSize,device):
        hc = (torch.FloatTensor(self.numLayersRhythmLSTM, currentBatchSize, self.hiddenSizeRhythm).normal_().to(device),
                torch.FloatTensor(self.numLayersRhythmLSTM, currentBatchSize, self.hiddenSizeRhythm).normal_().to(device) )
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

    def forward(self, midi, pitchClass, rhythm, currentBatchSize,device, hiddenMidi = None, hiddenRhythm = None):
        # midi size = pitchClass size = batch x voices x window
        # rhythm size = batch x 1 x window
        # First embed everythin
        #batchSize = midi.shape[0]
        #window = midi.shape[2]
        #print(pitchClass.shape)
        #if torch.max(pitchClass) <12:
        #    print(f"max of midi = {torch.max(midi)} max of pitchClass = {torch.max(pitchClass)} max of rhythm = {torch.max(rhythm)} ")
            #raise
        #print(f" input {midi[0,:,:]}   ")#statistcs {torch.mean(5)}")
        
        if hiddenMidi is None:
            hiddenMidi = self.init_hiddenMidi(currentBatchSize,device)
        else:
            hiddenMidi = self.repackage_hidden(hiddenMidi)
        
        print(f"input is {midi} {pitchClass} {rhythm}")
        # keep only the first voice for MONO
        if self.voices == 1:
            midi = midi[:,0,:]#.unsqueeze(1) # this is only because of mono
            pitchClass = pitchClass[:,0,:]
        # embeddings for midi , pitch , rhythm
        midiEmb = self.embMidi(midi) # batch x voice x window x embSize
        # print(f"midiEmb {torch.mean(midiEmb)}")

        pitchClassEmb = self.embPitchClass(pitchClass) # batch x voice x window x embSizePitchClass
        rhythmEmb = self.embRhythm(rhythm) # batch x 1 x window x embSizeRhythm

        # Reshape all embs / concatenate 2 voice dimensions into 1
        if self.voices == 2:
            midiEmb = torch.cat((midiEmb[:,0,:,:],midiEmb[:,1,:,:]),dim=2)
            pitchClassEmb = torch.cat((pitchClassEmb[:,0,:,:],pitchClassEmb[:,1,:,:]),dim=2)
        #rhythmEmb = rhythmEmb.view((rhythmEmb.shape[0],rhythmEmb.shape[2],-1))

        # combine the inputs
        # totalInput = midiEmb + pitchClassEmb
        # # And for rhythm LSTM
        # inputRhythmLstm = rhythmEmb
        #  midiEmb = 16, 128, 150 for mono
        
        if self.concatInputs:
            if self.includeRhythm:
                totalInp = torch.cat((midiEmb,pitchClassEmb,rhythmEmb[:,0,:,:]),dim=2)
            else:
                totalInp = torch.cat((midiEmb,pitchClassEmb),dim=2)
        else:
            if self.includeRhythm:
                totalInp = torch.cat(((midiEmb + pitchClassEmb), rhythmEmb[:,0,:,:]),dim=2)
            else:
                totalInp = midiEmb + pitchClassEmb
        # Load embs in the two LSTMs
        # First for midi LSTM 
        totalInp = self.dropoutEmb(totalInp) #+ pitchClassEmb
        print(f"totalInp {torch.mean(totalInp)}")
        lstmOutMidi, hiddenOutMidi = self.LstmMidi(totalInp, hiddenMidi) 
        #lstmOutRhythm, hiddenOutRhythm = self.LstmRhythm(inputRhythmLstm, hiddenRhythm) 

        # Reshape outputs 
        lstmOutMidiDense = lstmOutMidi.contiguous().view(-1,lstmOutMidi.shape[2])
        #lstmOutRhythmDense = lstmOutRhythm.contiguous().view(-1,lstmOutRhythm.shape[2])
        lstmOutMidiDense = self.dropoutLstm(lstmOutMidiDense)
        # Apply dense layers
        outLogits = self.fc1(lstmOutMidiDense)
        output = {
            'midi':{
                'midiBeforeFc' : lstmOutMidiDense,
                'logits':outLogits,
                'softmax':self.softmax(outLogits),
                'logSoftmax':self.logSoftmax(outLogits)
            },
            'misc' : 1,
            'hiddenOut':{
                'midi':hiddenOutMidi,
                'rhythm':hiddenRhythm, 
            }
        }
        return output
        #return outLogits, outSoftmax, outLogSoftmax, hiddenOutMidi, hiddenRhythm, 0

