# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 02:32:34 2018

@author: faidra
"""
import json
import torch
import numpy as np
from ParsingClasses import Part, TimeSignature, Duet, Piece, RhythmTemplate
from ParsingClasses import Note as Note2# from music21 import stream , instrument, note, duration, clef, layout, metadata
# from visdom import Visdom
from pathlib import Path
import pickle
# from music21 import *
# import matplotlib.pyplot as plt

def part2Tensor(part,vocabMidiArticGlobal,vocabRhythmGlobal):
    partTensor = torch.zeros((len(part.noteList),4))
    
    midiArtic1 = part.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
    pitchClass1 = part.getNoteList(mode = 'pitchClass')
    rhythm = part.getRhythmList(mode = 'rhythmIndex' , vocabulary = vocabRhythmGlobal)
    artic1 = part.getNoteList(mode = 'articulation')
    partTensor[:,0] = torch.tensor(midiArtic1)
    partTensor[:,1] = torch.tensor(pitchClass1)
    partTensor[:,2] = torch.tensor(rhythm)
    partTensor[:,3] = torch.tensor(artic1)
    return partTensor

def duetTokensToStream(duetTokensClass, vocabulary,mode):
    if duetTokensClass.__class__.__name__ == 'Duet':
        #print("gsrgsr")
        duetTokens = np.vstack((np.array(duetTokensClass.part1.getNoteList(mode='indexMidiArtic',vocabulary = vocabulary)),
                                   np.array(duetTokensClass.part2.getNoteList(mode='indexMidiArtic',vocabulary = vocabulary))
                                   ))
        colorInfo1 = np.array([note.isFermata for note in duetTokensClass.part1.noteList])
        colorInfo2 = np.array([note.isFermata for note in duetTokensClass.part2.noteList])
        print(colorInfo1)
        print(colorInfo2)
    # we expect to have size batchSize x Voices x SeqLen
    #duetTokens = duetTokens.squeeze(0)
    # find hit indexes and durations
    hits1=[]
    hits2=[]
    for i in range(duetTokens.shape[1]):
        if int(vocabulary.index2token[duetTokens[0,i]].split('_')[1])==1:
            hits1.append(i)
    for i in range(duetTokens.shape[1]):
        if int(vocabulary.index2token[duetTokens[1,i]].split('_')[1])==1:
            hits2.append(i)
    #hits1 = [i  for i in range(duetTokens.shape[1]) if int(vocabulary.index2token[duetTokens[0,i]].split('_')[1])==1]
    #hits2 = [i for i in range(duetTokens.shape[1]) if int(vocabulary.index2token[duetTokens[1,i]].split('_')[1])==1]
    hits1.append(duetTokens.shape[1])
    hits2.append(duetTokens.shape[1])
    dur1 = [hits1[i+1]-hits1[i] for i in range(0,len(hits1)-1)]
    dur2 = [hits2[i+1]-hits2[i] for i in range(0,len(hits2)-1)]
    
    voice1 = duetTokens[0,hits1[:-1]]
    voice2 = duetTokens[1,hits2[:-1]]
    colorInfo1 = colorInfo1[hits1[:-1]]
    colorInfo2 = colorInfo2[hits2[:-1]]
    notesCount1 = len(voice1)
    notesCount2 = len(voice2)
    dur16 = duration.Duration()
    dur16.quarterLength = 1/4
    s = stream.Score()
    part1 = stream.Part()
    part2 = stream.Part()
    if mode==1:
        part1.insert(instrument.Flute())
        part2.insert(instrument.Violoncello())
    else:
        part2.insert(instrument.Flute())
        part1.insert(instrument.Violoncello())
	
    for i in range(notesCount1):
        tempMidi1 = int(vocabulary.index2token[voice1[i]].split('_')[0])
        if tempMidi1 == 0:
            n1 = note.Rest()
            n1.duration = dur16
        else:
            n1 = note.Note(midi = int(tempMidi1))
            tempDur = duration.Duration()
            tempDur.quarterLength = 1/4 * dur1[i]
            n1.duration = tempDur
            #print(colorInfo1.__class__.__name__)
            if isinstance(colorInfo1[i],str):
                n1.style.color = colorInfo1[i]
                #print("red1")
        part1.append(n1)
    for i in range(notesCount2): 
        tempMidi2 = int(vocabulary.index2token[voice2[i]].split('_')[0])
        if tempMidi2 == 0:
            n2 = note.Rest()
            n2.duration = dur16
        else:
            n2 = note.Note(midi = int(tempMidi2))
            tempDur = duration.Duration()
            tempDur.quarterLength = 1/4 * dur2[i]
            n2.duration = tempDur
            if isinstance(colorInfo2[i],str):
                n2.style.color = colorInfo2[i]
                #print("red2")
        part2.append(n2)
    b = clef.bestClef(part2)
    part2.insert(0,b)
    print(part1)
    s.insert(0, part1)   
    s.insert(0, part2)
    s.insert(0, metadata.Metadata())
    s.metadata.title = duetTokensClass.metadata.title
    s.metadata.parentTitle = duetTokensClass.metadata.pieceType
    s.metadata.opusNumber = 'familyIndex = ' + str(duetTokensClass.metadata.familyIndex)
    s.metadata.sceneNumber = 'uniqIndex = ' + str(duetTokensClass.metadata.uniqIndex)
    staffGroup1 = layout.StaffGroup([part1, part2], name='Marimba', abbreviation='Mba.', symbol='brace')
    #staffGroup1.barTogether = 'Mensurstrich'
    s.insert(0, staffGroup1)
    return s

class Params():
    """Class that loads hyperparameters from a json file.
    Example:
    ```
    params = Params(json_path)
    print(params.learning_rate)
    params.learning_rate = 0.5  # change the value of learning_rate in params
    ```
    """

    def __init__(self, json_path):
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    def save(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']"""
        return self.__dict__
def rename(old_dict,old_name,new_name):
    new_dict = {}
    for key,value in zip(old_dict.keys(),old_dict.values()):
        new_key = key if key != old_name else new_name
        new_dict[new_key] = old_dict[key]
    return new_dict
def push2tensor(a,b,dim):
    if dim == 0 :
        aNew = a[1:,:,:]
    elif dim == 1:
        aNew = a[:,1:,:]
    elif dim == 2:
        aNew = a[:,:,1:]
    return torch.cat((aNew, b),dim)
class TensorBuffer():
    def __init__(self, maxLen, shape, restIndex, device, typeTensor = 'long'):
        # self.tensorBuffer = TensorBuffer(maxLen=2, shape = [2,1], restIndex=self.restTokenIndex, device=self.device)
        self.voices = shape[0]
        self.features = shape[1]
        self.maxLen = maxLen
        self.shape = shape.append(maxLen)
        self.restIndex = restIndex
        self.device = device
        self.typeTensor = typeTensor
        if typeTensor == 'float':
            self.data = torch.Tensor(self.voices,self.features,self.maxLen).fill_(1).to(self.device).float() * self.restIndex #torch.ones(self.shape)
        else:
            self.data = torch.LongTensor(self.voices,self.features,self.maxLen).fill_(1).to(self.device) * self.restIndex #torch.ones(self.shape)
    def push(self, newElements):
        if self.typeTensor == 'float':
            newEntry = torch.Tensor(newElements).unsqueeze(1).unsqueeze(2).float().to(self.device)
        else:
            newEntry = torch.LongTensor(newElements).unsqueeze(1).unsqueeze(2).to(self.device)
        self.data = torch.cat((self.data[...,1:],newEntry), 2)
    def pushTest(self, newElements):
        newEntry = torch.LongTensor(newElements).unsqueeze(2).to(self.device)
        self.data = torch.cat((self.data[...,1:],newEntry), 2)
    def clear(self):
        if self.typeTensor == 'float':
            self.data = torch.Tensor(self.voices,self.features,self.maxLen).fill_(1).float().to(self.device) * self.restIndex #torch.ones(self.shape)
        else:
            self.data = torch.LongTensor(self.voices,self.features,self.maxLen).fill_(1).to(self.device) * self.restIndex
class tensorFIFO():
    def __init__(self,maxLen,shape,restIndex):
        # maxLen  = maximum number of elements of shape self.shape
        self.maxLen = maxLen
        self.shape = shape
        self.restIndex = restIndex
        self.totalQueueShape = self.shape.copy()
        self.totalQueueShape.append(self.maxLen)
        self.queue = torch.ones(self.totalQueueShape).type(torch.cuda.LongTensor) * self.restIndex
        self.dim = len(self.shape)
    def push(self,newElement):
        if list(newElement.shape) != self.shape:
            print(f"element size should be {self.shape}")
            return 0
        self.queue = torch.cat((self.queue[...,1:],newElement.unsqueeze(self.dim)),self.dim)
        return self.queue
    def init(self, voice1=None, voice2=None, size=0, restsBefore=True):
        if restsBefore:
            self.queue = torch.ones(self.totalQueueShape).type(torch.cuda.LongTensor) * self.restIndex
        if voice1 is not None:
            for i in range(size):
                #self.queue[:,0,:] = voice1
                self.queue[...,0,:] = torch.cat((self.queue[...,0,1:].squeeze(),voice1[i].unsqueeze(0)),0)
        if voice2 is not None:
            for i in range(size):
                #self.queue[:,0,:] = voice1
                self.queue[...,1,:] = torch.cat((self.queue[...,1,1:].squeeze(),voice2[i].unsqueeze(0)),0)
        return self.queue
    def init2(self, voice1=None, voice2=None, size=0, restsBefore=True):
        if restsBefore:
            self.queue = torch.ones(self.totalQueueShape).type(torch.cuda.LongTensor) * self.restIndex
        aaaa = self.queue[0,0,:]
        bbbb = self.queue[0,1,:]
        if voice1 is not None:
            for i in range(size):
                #self.queue[:,0,:] = voice1
                aaaa = torch.cat((aaaa.squeeze(),voice1[i].unsqueeze(0)),0)
        if voice2 is not None:
            for i in range(size):
                #self.queue[:,0,:] = voice1
                bbbb = torch.cat((bbbb.squeeze(),voice2[i].unsqueeze(0)),0)
        #print(aaaa.shape)
        #print(aaaa.unsqueeze(0).shape)
        self.queue = torch.cat((aaaa.unsqueeze(0).unsqueeze(0),bbbb.unsqueeze(0).unsqueeze(0)),1)
        return self.queue

def accuracy(output, target):
    with torch.no_grad():
        pred = torch.argmax(output, dim=1)
        assert pred.shape[0] == len(target)
        #correct = 0
        correct = (pred == target).sum().item()
    return correct / len(target)

def ind2Hot(target, vocSize):
    batchSize = len(target)
    b = np.zeros((batchSize, vocSize))
    b[np.arange(len(target)), target] = 1
    return b

def sliding_window_view(arr, shape, step, addLast):
    voices = arr.shape[0]
    #print(voices)
    n = np.array(arr.shape) 
    o = n - shape + 1 # output shape
    strides = arr.strides

    new_shape = np.concatenate((o, shape), axis=0)
    new_strides = np.concatenate((strides, strides), axis=0)
    result = np.lib.stride_tricks.as_strided(arr ,new_shape, new_strides)[:,::step, :][0,:,:,:]
    if addLast:
        #print(result.shape)
        #print(arr[:,-shape[1]:].reshape(1,2,shape[1]).shape)
        result = np.vstack((result,arr[:,-shape[1]:].reshape(1,voices,shape[1])))
    return result

def extend(duet,size,addRest, mode):
    extension = None
    if mode == 'rhythm':
        rhythmList = [i for i in duet[0,:]]
        indexes = [i for i, j in enumerate(rhythmList) if j == '1_0_0']
        period = indexes[1]-indexes[0]
        lastIndex = indexes[-1]
        currentIndex = len(rhythmList)
        # find difference between last index of starting measure, and currentIndex
        diff = currentIndex - lastIndex
        diffPer = period - diff
        mult = int(size / len(rhythmList)) + 1
        rhythmListForSlicing = rhythmList*mult
    if addRest:
        if size <=4:
            if mode == 'note':
                extension = np.array([Note(midi = 0,articulation=1,pitchClass=12) for i in range(2*size)]).reshape(2,-1)
            elif mode == 'rhythm':
                # get rhythm List
                # find indexes of '1_0_0'
                extRhythm = rhythmListForSlicing[indexes[2]-diffPer:indexes[2]-diffPer + size]
                extension = np.array(extRhythm).reshape(1,-1)
            size = 0
        else:
            if mode == 'note':
                extension = np.array([Note(midi = 0,articulation=1,pitchClass=12) for i in range(2*4)]).reshape(2,-1)
            if mode == 'rhythm':
                extRhythm = rhythmListForSlicing[indexes[2]-diffPer:indexes[2]-diffPer + 4]
                extension = np.array(extRhythm).reshape(1,-1)
            size = size - 4
    if size > 0 :
        if mode == 'note':
            if extension is not None:
                extension = np.hstack((extension,duet[:,0:size]))
            else:
                extension = duet[:,0:size]
        if mode == 'rhythm':
            aa = np.array([rhythmList[0:size]])
            if extension is not None:
                extension = np.hstack((extension,aa))
            else:
                extension = aa
    
    return np.hstack((duet,extension))

def segmentDuetsHelper(segmentedDuets,i,duet,win,hop,totalSamples):
    
    
    if len(duet.part1.rhythmList) != len(duet.part1.noteList):
        raise
    half = int(win//2)
    overlap = int(np.random.randint(half//2, 3*half//2, 1))
    step = win - overlap
    if hop is not None:
        step = hop
#        print(i)
#        if i == 7996:
#            aaa = 3333
    voice1 = duet.part1
    voice2 = duet.part2
    rhythm = duet.part1.rhythmList
    numpyNotes = np.array([voice1.noteList, voice2.noteList])
    numpyRhythm = np.array([rhythm])
    tempLen = len(voice1.noteList)
    diff = tempLen-win-1
    if diff <=0:
        numpyNotes = extend(numpyNotes,size = -diff, addRest = 1, mode = 'note')
        numpyRhythm = extend(numpyRhythm,size = -diff, addRest = 1, mode = 'rhythm')
        addLast = 0
    elif diff == 0:
        #tempPitchClassDuet = extend(tempPitchClassDuet,size = 1, rests = 1)
        addLast = 0
    elif diff > 0:
        addLast = 1
        #tempPitchClassDuet = extend(tempPitchClassDuet, size = diff, rests = 0)
    numpyNotesSegmented = sliding_window_view(numpyNotes,[2,win+1],step = step,addLast = addLast)
    numpyRhythmSegmented = sliding_window_view(numpyRhythm, [1,win+1],step = step, addLast = addLast)
    totalSamples += len(numpyNotesSegmented)
    # create (segmented) parts and Duet again, and put it in the list
    for ind, numpyDuet in enumerate(numpyNotesSegmented):
        # create segmented Parts
        part1 = Part(noteList = list(numpyDuet[0,:]), instrument = voice1.instrument, metadata = duet.metadata,
                     rhythmList = [ee for ee in numpyRhythmSegmented[ind,0,:]], timeSignature = voice1.timeSignature )
        part2 = Part(noteList = list(numpyDuet[1,:]), instrument = voice2.instrument, metadata = duet.metadata,
                     rhythmList = [ee for ee in numpyRhythmSegmented[ind,0,:]], timeSignature = voice2.timeSignature )
                     
                 
        tempDuetSegmented = Duet(parts = [part1, part2], metadata = duet.metadata, timeSignature = duet.timeSignature)
        
        segmentedDuets.append(tempDuetSegmented)
    #segmentedDuets.append(numpyNotesSegmented)
#len(choralesDuet[7998].part1.rhythmList)
    #del duet
    return segmentedDuets, totalSamples
def segmentDuets(inputDuets, win, hop=None): 
    segmentedDuets=[]  
    totalSamples = 0
    ll = len(inputDuets)
    for i in range(ll):
        print(f"win = {win} {i}/{ll}")
        duet = inputDuets[i]
        segmentedDuets,totalSamples = segmentDuetsHelper(segmentedDuets,i,duet,win,hop,totalSamples)
    return segmentedDuets    

def duet2Tensor(duets,vocabMidiArticGlobal,vocabRhythmGlobal):
    duetTensor = torch.zeros((4,len(duets),2,len(duets[0].part1.noteList)))
    for i,duet in enumerate(duets):
        midiArtic1 = duet.part1.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        midiArtic2 = duet.part2.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        pitchClass1 = duet.part1.getNoteList(mode = 'pitchClass')
        pitchClass2 = duet.part2.getNoteList(mode = 'pitchClass')
        rhythm = duet.part1.getRhythmList(mode = 'rhythmIndex' , vocabulary = vocabRhythmGlobal)
        artic1 = duet.part1.getNoteList(mode = 'articulation')
        artic2 = duet.part2.getNoteList(mode = 'articulation')
        uuid = duet.metadata.uniqIndex
        famInd = duet.metadata.familyIndex
        #print(midiArtic1)
        duetTensor[0,i,0,:] = torch.tensor(midiArtic1)
        duetTensor[0,i,1,:] = torch.tensor(midiArtic2)
        duetTensor[1,i,0,:] = torch.tensor(pitchClass1)
        duetTensor[1,i,1,:] = torch.tensor(pitchClass2)
        duetTensor[2,i,0,:] = torch.tensor(artic1)
        duetTensor[2,i,1,:] = torch.tensor(artic2)
        duetTensor[3,i,0,:] = torch.tensor(rhythm)
        duetTensor[3,i,1,0] = uuid
        duetTensor[3,i,1,1] = famInd
    return duetTensor
def duet2TensorConcat(duets, vocabMidiArticGlobal, vocabRhythmGlobal, vocabKeysGlobal, shuffle=1):
    voices = 2
    if hasattr(duets[0], 'part3'):
        voices = 3
    totalLength = sum([duet.part1.getSize() for duet in duets])
    duetTensor = torch.zeros(4,voices,totalLength)
    start = 0
    inds = np.arange(len(duets))
    if shuffle:
        np.random.shuffle(inds)
    for ind in inds:
        duet = duets[ind]
        midiArtic1 = duet.part1.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        midiArtic2 = duet.part2.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        
        pitchClass1 = duet.part1.getNoteList(mode = 'pitchClass')
        pitchClass2 = duet.part2.getNoteList(mode = 'pitchClass')
        
        rhythm = duet.part1.getRhythmList(mode = 'rhythmIndex' , vocabulary = vocabRhythmGlobal)
        artic1 = duet.part1.getNoteList(mode = 'articulation')
        artic2 = duet.part2.getNoteList(mode = 'articulation')
        if voices == 3:
            midiArtic3 = duet.part3.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
            pitchClass3 = duet.part3.getNoteList(mode = 'pitchClass')
            artic3 = duet.part3.getNoteList(mode = 'articulation')
        keys = duet.part1.getKeyList(mode = 'keyIndex', vocabulary = vocabKeysGlobal)
        uuid = duet.metadata.uniqIndex
        famInd = duet.metadata.familyIndex
        currentLength = len(midiArtic1)
        end = start + currentLength
        duetTensor[0,0,start:end] = torch.tensor(midiArtic1)
        duetTensor[0,1,start:end] = torch.tensor(midiArtic2)
        if voices == 3:
            try:
                duetTensor[0,2,start:end] = torch.tensor(midiArtic3)
            except:
                print(duet.part3.metadata.__dict__)
                raise
            duetTensor[1,2,start:end] = torch.tensor(pitchClass3)
            duetTensor[2,2,start:end] = torch.tensor(artic3)
        duetTensor[1,0,start:end] = torch.tensor(pitchClass1)
        duetTensor[1,1,start:end] = torch.tensor(pitchClass2)
        duetTensor[2,0,start:end] = torch.tensor(artic1)
        duetTensor[2,1,start:end] = torch.tensor(artic2)
        duetTensor[3,0,start:end] = torch.tensor(rhythm)
        duetTensor[3,1,start:end] = torch.tensor(keys)
        # duetTensor[3,1,0] = uuid
        # duetTensor[3,1,1] = famInd
        # duetTensor[3,1,2] = currentLength
        start = end
    return duetTensor
def duet2TensorNotSegm(duets,vocabMidiArticGlobal,vocabRhythmGlobal):
    eachDuetsLength = [len(duets[i].part1.noteList) for i in range(len(duets))]
    duetTensor = torch.zeros((4,len(duets),2,max(eachDuetsLength)))-1
    for i,duet in enumerate(duets):
        midiArtic1 = duet.part1.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        midiArtic2 = duet.part2.getNoteList(mode = 'indexMidiArtic', vocabulary = vocabMidiArticGlobal)
        pitchClass1 = duet.part1.getNoteList(mode = 'pitchClass')
        pitchClass2 = duet.part2.getNoteList(mode = 'pitchClass')
        rhythm = duet.part1.getRhythmList(mode = 'rhythmIndex' , vocabulary = vocabRhythmGlobal)
        artic1 = duet.part1.getNoteList(mode = 'articulation')
        artic2 = duet.part2.getNoteList(mode = 'articulation')
        uuid = duet.metadata.uniqIndex
        famInd = duet.metadata.familyIndex
        #print(midiArtic1)
        currentLength = eachDuetsLength[i]
        duetTensor[0,i,0,0:currentLength] = torch.tensor(midiArtic1)
        duetTensor[0,i,1,0:currentLength] = torch.tensor(midiArtic2)
        duetTensor[1,i,0,0:currentLength] = torch.tensor(pitchClass1)
        duetTensor[1,i,1,0:currentLength] = torch.tensor(pitchClass2)
        duetTensor[2,i,0,0:currentLength] = torch.tensor(artic1)
        duetTensor[2,i,1,0:currentLength] = torch.tensor(artic2)
        duetTensor[3,i,0,0:currentLength] = torch.tensor(rhythm)
        duetTensor[3,i,1,0] = uuid
        duetTensor[3,i,1,1] = famInd
        duetTensor[3,i,1,2] = currentLength # will use that for packed sequences in pytorch
    return duetTensor
def addErrorsTensor2(batchTensor, prob, vocabMidiArticGlobal, listInp = 1, exclude = [2]):
    # batchTensor = features, voices, batchSize, length
    restIndex = vocabMidiArticGlobal.token2index['0_1']
    batchNoise = batchTensor.clone()
    for i in range(batchNoise.shape[2]):#enumerate(batchList):
        #correctDuet = alfa[:,i,:,:]
        correctDuet = batchTensor[:,:,i,:]
        errorDuet = correctDuet.clone()
        #Get Hit information
        # these temp vars will change as errors are added in errorDuet
        tempIndexMidi = errorDuet[0,:,:] 
        #tempPitchClass = errorDuet[1,:,:]
        tempHit = errorDuet[2,:,:]
        # Get indexes of Hits
        hitsOfRests =  torch.where(tempIndexMidi == restIndex, torch.zeros(tempHit.size()),torch.ones(tempHit.size()))
        validHits = tempHit * hitsOfRests
        hitIndex = validHits.nonzero()
        hitIndexShuffled = hitIndex[torch.randperm(hitIndex.shape[0]),:]
        # Count Hits (except of hits of Rests)
        N = torch.sum(validHits)
        # E = the number of hits where I ll apply noie
        E = np.random.binomial(N,prob,1)
        
        
        # Error Type selection
        errorType = np.random.randint(0,3,E,np.int8)
        # Random commands for replace
        replaceCommands = np.random.randint(0,3,E,np.int8)
        replaceCommands[replaceCommands==0] = 1
        #  Random commands for insertion
        insertionCommandPitch = np.random.randint(-2,3,E,np.int8)
        insertionCommandPos = np.random.randint(-2,0,E,np.int8)
        insertionCommandPos[insertionCommandPos==0] = -1
        # total nota length of duet
        totalLength = tempHit.shape[1]
        # Apply the noise
        printare = False
        for j in range(E[0]):
            
            index = hitIndexShuffled[j,:]
            voice = index[0].item()
            nota =  index[1].item()
            if int(errorDuet[0,voice,nota].item()) == restIndex:
                #print(f"diavasa paush {j}")
                printare = True
                continue
            foundNextHit = False
            foundPrevHit = False
            tempDur16 = 1
            tempHoldsBefore = 0
            k = nota
            # find duration of note
            while (not foundNextHit) and (k<totalLength-1):
                k += 1
                if errorDuet[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    #if errorDuet[0,voice,k] != restIndex
                    foundNextHit = True
                else:
                    tempDur16 +=1
            k = nota
            # find holds before the note
            while (not foundPrevHit) and (k>0):
                k -= 1
                if  errorDuet[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    if int(errorDuet[0,voice,k].item()) != restIndex: # isws na fygei ayto ? 
                        foundPrevHit = True
                else:
                    tempHoldsBefore +=1
    
            if errorType[j] == 0: # Replace
                pitchShift = replaceCommands[j]
                
                newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorDuet[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 92 or newMidi < 31:
                    #print(f"before newMidi was {newMidi}")
                    newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) - pitchShift
                    #print(f"after newMidi was {newMidi}")
                    newPitchClass = (errorDuet[1,voice,nota].item() - pitchShift.item())%12
    
                for v in range(tempDur16):
                    #print(f"finally newMidi was {newMidi}")
                    errorDuet[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(int(errorDuet[2,voice,nota+v].item()))]
                    errorDuet[1,voice,nota+v] = newPitchClass
            elif errorType[j] == 1: #DELETION
                newIndexMidi = restIndex
                newPitchClass = 12
                for v in range(tempDur16):
                    errorDuet[0,voice,nota+v] = newIndexMidi
                    errorDuet[1,voice,nota+v] = newPitchClass
                    errorDuet[2,voice,nota+v] = 1 # articulation is1 in rests
            elif errorType[j] == 2: #INSERTION
                pitchShift = insertionCommandPitch[j]
                newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorDuet[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 92 or newMidi < 31:
                    #print(f"before newMidi was {newMidi}")
                    newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) - pitchShift
                    #print(f"after newMidi was {newMidi}")
                    newPitchClass = (errorDuet[1,voice,nota].item() - pitchShift.item())%12
                newPos = insertionCommandPos[j].item()
                if newPos < 0 and abs(newPos)<tempHoldsBefore:
                    for v in range(newPos,0):
                        newArtic = 0
                        if v == newPos:
                            newArtic = 1
                        #print(f"finally newMidi was {newMidi}")
                        errorDuet[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(newArtic)]
                        errorDuet[1,voice,nota+v] = newPitchClass
                        errorDuet[2,voice,nota+v] = newArtic
        batchNoise[:,:,i,:]=errorDuet
    return batchNoise
def addShifts(errorPiece, partPos, partInd , prob , vocabMidiArticGlobal):
    restIndex = vocabMidiArticGlobal.token2index['0_1']
    # Count Hits (except of hits of Rests)
    N = partPos.shape[0]
    # E = the number of hits where I ll apply noie
    E = np.random.binomial(N,prob,1)
    totalLength = errorPiece.shape[2]
    
    shift = np.random.randint(-1,3,E,np.int8)
    shift[shift==0] = +1
    #print(E)
    for j in range(E[0]):
        voice = partInd
        index =  partPos[j]
        if int(errorPiece[0,voice,index].item()) == restIndex:
            #print(f"diavasa paush {j}")
            printare = True
            continue
        foundNextHit = False
        foundPrevHit = False
        tempDur16 = 1
        tempHoldsBefore = 0
        k = index
        # find duration of note
        while (not foundNextHit) and (k<totalLength-1):
            k += 1
            if errorPiece[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                #if errorDuet[0,voice,k] != restIndex
                foundNextHit = True
            else:
                tempDur16 +=1
        # find holds before the note
        k = index
        while (not foundPrevHit) and (k>0):
            k -= 1
            if  errorPiece[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                if int(errorPiece[0,voice,k].item()) != restIndex: # isws na fygei ayto ? 
                    foundPrevHit = True
            else:
                tempHoldsBefore +=1
        
        if tempDur16 == 1 and tempHoldsBefore == 0:
            continue
        tempShift = shift[j]
        if tempShift > 0:
            actualShift = min(tempShift, tempDur16-1)
            errorPiece[:,voice,index+actualShift] = errorPiece[:,voice,index]
            errorPiece[:,voice,index:index+actualShift] = errorPiece[:,voice,index-1]
            partPos[j] += actualShift
        if tempShift < 0:
            actualShift = min(-tempShift, tempHoldsBefore)
            partPos[j] -= actualShift
            errorPiece[:,voice,index-actualShift]  = errorPiece[:,voice,index]
            errorPiece[:,voice,index-actualShift+1:index+1] = errorPiece[:,voice,index+1]
    return errorPiece, partPos

def addErrorsTensor3(batchTensor, vocabMidiArticGlobal, probNoise=0.1, probShift = 0.5,  listInp = 1, exclude = [2]):
    # batchTensor = features, voices, batchSize, length
    restIndex = vocabMidiArticGlobal.token2index['0_1']
    batchNoise = batchTensor.clone()
    indexMidiBatch = batchNoise[0,:,:,:]
    articHitBatch = batchNoise[2,:,:,:]
    restHitsBatch =  torch.where(indexMidiBatch == restIndex, torch.zeros(articHitBatch.size()),torch.ones(articHitBatch.size()))
    validHitsBatch = articHitBatch * restHitsBatch
    voices = batchNoise.shape[1]
    for i in range(batchNoise.shape[2]):#enumerate(batchList):
        part1Pos = validHitsBatch[0,i,:].nonzero()
        part1Pos = part1Pos[torch.randperm(part1Pos.shape[0]),:]
        
        part2Pos = validHitsBatch[1,i,:].nonzero()
        part2Pos = part2Pos[torch.randperm(part2Pos.shape[0]),:]
        
        if part1Pos.shape[0] == 0 or part2Pos.shape[0] == 0:
            continue
        
        if voices ==3:
            part3Pos = validHitsBatch[2,i,:].nonzero()
            part3Pos = part3Pos[torch.randperm(part3Pos.shape[0]),:]
            if part3Pos.shape[0] == 0 :
                continue
        errorPiece = batchNoise[:,:,i,:]
        #####################################################################
        ########### Shift back and forth 1/16 for part2 (human) #############
        #####################################################################
        errorPiece, part2Pos= addShifts(errorPiece = errorPiece, partPos = part2Pos, partInd = 1, prob = probShift, vocabMidiArticGlobal = vocabMidiArticGlobal)
        try:
            part1Pos = torch.cat((part1Pos, torch.tensor([0]).repeat(part1Pos.shape[0]).unsqueeze(1)), dim=1)
            part2Pos = torch.cat((part2Pos, torch.tensor([1]).repeat(part2Pos.shape[0]).unsqueeze(1)), dim=1)
        except:
            print(part1Pos.shape)
            print(torch.tensor([0]).repeat(part1Pos.shape[0]).unsqueeze(1).shape)
            print(part2Pos.shape)
            print(torch.tensor([0]).repeat(part2Pos.shape[0]).unsqueeze(1).shape)
            raise
        
        if voices == 3:
            part3Pos = torch.cat((part3Pos, torch.tensor([2]).repeat(part3Pos.shape[0]).unsqueeze(1)), dim=1)
            allPos = torch.cat((part1Pos,part2Pos, part3Pos),dim=0)
        elif voices == 2:
            allPos = torch.cat((part1Pos,part2Pos),dim=0)
        allPos = allPos[torch.randperm(allPos.shape[0]),:]
        ### now the same as the old addErrors
        # Count Hits (except of hits of Rests)
        N = allPos.shape[0]
        # E = the number of hits where I ll apply noie
        E = np.random.binomial(N,probNoise,1)
        # Error Type selection
        errorType = np.random.randint(0,4,E,np.int8)
        # Random commands for replace
        replaceCommands = np.random.randint(0,3,E,np.int8)
        replaceCommands[replaceCommands==0] = 1
        #  Random commands for insertion
        insertionCommandPitch = np.random.randint(-2,3,E,np.int8)
        insertionCommandPos = np.random.randint(-2,0,E,np.int8)
        insertionCommandPos[insertionCommandPos==0] = -1
        # total nota length of duet
        totalLength = errorPiece.shape[2]
        # Apply the noise
        printare = False

        for j in range(E[0]):
            
            index = allPos[j,:]
            voice = index[1].item()
            nota =  index[0].item()
            if int(errorPiece[0,voice,nota].item()) == restIndex:
                #print(f"diavasa paush {j}")
                printare = True
                continue
            foundNextHit = False
            foundPrevHit = False
            tempDur16 = 1
            tempHoldsBefore = 0
            k = nota
            # find duration of note
            while (not foundNextHit) and (k<totalLength-1):
                k += 1
                if errorPiece[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    #if errorDuet[0,voice,k] != restIndex
                    foundNextHit = True
                else:
                    tempDur16 +=1
            # find holds before the note
            while (not foundPrevHit) and (k>0):
                k -= 1
                if  errorPiece[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    if int(errorPiece[0,voice,k].item()) != restIndex: # isws na fygei ayto ? 
                        foundPrevHit = True
                else:
                    tempHoldsBefore +=1
    
            if errorType[j] == 0: # Replace
                pitchShift = replaceCommands[j]
                
                newMidi = int(vocabMidiArticGlobal.index2token[errorPiece[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorPiece[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 92 or newMidi < 31:
                    #print(f"before newMidi was {newMidi}")
                    newMidi = int(vocabMidiArticGlobal.index2token[errorPiece[0,voice,nota].item()].split('_')[0]) - pitchShift
                    #print(f"after newMidi was {newMidi}")
                    newPitchClass = (errorPiece[1,voice,nota].item() - pitchShift.item())%12
    
                for v in range(tempDur16):
                    #print(f"finally newMidi was {newMidi}")
                    errorPiece[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(int(errorPiece[2,voice,nota+v].item()))]
                    errorPiece[1,voice,nota+v] = newPitchClass
            elif errorType[j] == 1: #DELETION
                newIndexMidi = restIndex
                newPitchClass = 12
                for v in range(tempDur16):
                    errorPiece[0,voice,nota+v] = newIndexMidi
                    errorPiece[1,voice,nota+v] = newPitchClass
                    errorPiece[2,voice,nota+v] = 1 # articulation is1 in rests
            elif errorType[j] == 2: #INSERTION
                pitchShift = insertionCommandPitch[j]
                newMidi = int(vocabMidiArticGlobal.index2token[errorPiece[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorPiece[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 92 or newMidi < 31:
                    #print(f"before newMidi was {newMidi}")
                    newMidi = int(vocabMidiArticGlobal.index2token[errorPiece[0,voice,nota].item()].split('_')[0]) - pitchShift
                    #print(f"after newMidi was {newMidi}")
                    newPitchClass = (errorPiece[1,voice,nota].item() - pitchShift.item())%12
                newPos = insertionCommandPos[j].item()
                if newPos < 0 and abs(newPos)<tempHoldsBefore:
                    for v in range(newPos,0):
                        newArtic = 0
                        if v == newPos:
                            newArtic = 1
                        #print(f"finally newMidi was {newMidi}")
                        errorPiece[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(newArtic)]
                        errorPiece[1,voice,nota+v] = newPitchClass
                        errorPiece[2,voice,nota+v] = newArtic
            elif errorType[j] == 3: #Random note anywhere
                newInd = random.randint(0,vocabMidiArticGlobal.n_tokens-1)
                newPitchClass = 12 # fix that
                newArtic = int(vocabMidiArticGlobal.index2token[newInd].split('_')[1])
                newMidi = int(vocabMidiArticGlobal.index2token[newInd].split('_')[0])
                errorPiece[0,voice,nota] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(newArtic)]
                errorPiece[1,voice,nota] = newPitchClass
                errorPiece[2,voice,nota] = newArtic
        batchNoise[:,:,i,:] = errorPiece
    return batchNoise
def addErrorsTensor(batchList, prob, vocabMidiArticGlobal, listInp = 1):
    restIndex = vocabMidiArticGlobal.token2index['0_1']
    batchNoiseList = []
    for i,correctDuet in enumerate(batchList):
        #correctDuet = alfa[:,i,:,:]
        errorDuet = correctDuet.clone()
        #Get Hit information
        # these temp vars will change as errors are added in errorDuet
        tempIndexMidi = errorDuet[0,:,:] 
        #tempPitchClass = errorDuet[1,:,:]
        tempHit = errorDuet[2,:,:]
        # Get indexes of Hits
        hitsOfRests =  torch.where(tempIndexMidi == 96, torch.zeros(tempHit.size()),torch.ones(tempHit.size()))
        validHits = tempHit * hitsOfRests
        hitIndex = validHits.nonzero()
        hitIndexShuffled = hitIndex[torch.randperm(hitIndex.shape[0]),:]
        # Count Hits (except of hits of Rests)
        N = torch.sum(validHits)
        # E = the number of hits where I ll apply noie
        E = np.random.binomial(N,prob,1)
        
        
        # Error Type selection
        errorType = np.random.randint(0,3,E,np.int8)
        # Random commands for replace
        replaceCommands = np.random.randint(0,3,E,np.int8)
        replaceCommands[replaceCommands==0] = 1
        #  Random commands for insertion
        insertionCommandPitch = np.random.randint(-2,3,E,np.int8)
        insertionCommandPos = np.random.randint(-2,0,E,np.int8)
        insertionCommandPos[insertionCommandPos==0] = -1
        # total nota length of duet
        totalLength = tempHit.shape[1]
        # Apply the noise
        printare = False
        for j in range(E[0]):
            
            index = hitIndexShuffled[j,:]
            voice = index[0].item()
            nota =  index[1].item()
            if int(errorDuet[0,voice,nota].item()) == restIndex:
                #print(f"diavasa paush {j}")
                printare = True
                continue
            foundNextHit = False
            foundPrevHit = False
            tempDur16 = 1
            tempHoldsBefore = 0
            k = nota
            # find duration of note
            while (not foundNextHit) and (k<totalLength-1):
                k += 1
                if errorDuet[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    #if errorDuet[0,voice,k] != restIndex
                    foundNextHit = True
                else:
                    tempDur16 +=1
            # find holds before the note
            while (not foundPrevHit) and (k>0):
                k -= 1
                if  errorDuet[2,voice,k] == 1 : #tempHit[voice,k] == 1:
                    if int(errorDuet[0,voice,k].item()) != restIndex: # isws na fygei ayto ? 
                        foundPrevHit = True
                else:
                    tempHoldsBefore +=1
    
            if errorType[j] == 0: # Replace
                pitchShift = replaceCommands[j]
                
                newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorDuet[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 94 or newMidi < 28:
                    newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) - pitchShift
                    newPitchClass = (errorDuet[1,voice,nota].item() - pitchShift.item())%12
    
                for v in range(tempDur16):
                    errorDuet[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(int(errorDuet[2,voice,nota+v].item()))]
                    errorDuet[1,voice,nota+v] = newPitchClass
            elif errorType[j] == 1: #DELETION
                newIndexMidi = restIndex
                newPitchClass = 12
                for v in range(tempDur16):
                    errorDuet[0,voice,nota+v] = newIndexMidi
                    errorDuet[1,voice,nota+v] = newPitchClass
                    errorDuet[2,voice,nota+v] = 1 # articulation is1 in rests
            elif errorType[j] == 2: #INSERTION
                pitchShift = insertionCommandPitch[j]
                newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) + pitchShift
                newPitchClass = (errorDuet[1,voice,nota].item() + pitchShift.item())%12
                if newMidi > 94 or newMidi < 28:
                    newMidi = int(vocabMidiArticGlobal.index2token[errorDuet[0,voice,nota].item()].split('_')[0]) - pitchShift
                    newPitchClass = (errorDuet[1,voice,nota].item() - pitchShift.item())%12
                newPos = insertionCommandPos[j].item()
                if newPos < 0 and abs(newPos)<tempHoldsBefore:
                    for v in range(newPos,0):
                        newArtic = 0
                        if v == newPos:
                            newArtic = 1
                        errorDuet[0,voice,nota+v] = vocabMidiArticGlobal.token2index[str(newMidi)+'_'+str(newArtic)]
                        errorDuet[1,voice,nota+v] = newPitchClass
                        errorDuet[2,voice,nota+v] = newArtic
        batchNoiseList.append(errorDuet)
    return batchNoiseList

def factors(n): 
    # print(f"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee {n}")   
    return np.array(list(set(reduce(list.__add__,([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))))
def findBestWindow(n,ideal):
    # find factors
    fac = factors(n)
    ind = np.argmin(np.abs(fac - ideal))
    if (fac[ind]/ideal) <0.8:
        return ideal
    return fac[ind]
def sliding_window_view(arr, shape, step, addLast):
    voices = arr.shape[0]
    #print(voices)
    n = np.array(arr.shape) 
    o = n - shape + 1 # output shape
    strides = arr.strides

    new_shape = np.concatenate((o, shape), axis=0)
    new_strides = np.concatenate((strides, strides), axis=0)
    result = np.lib.stride_tricks.as_strided(arr ,new_shape, new_strides)[:,::step, :][0,:,:,:]
    if addLast:
        #print(result.shape)
        #print(arr[:,-shape[1]:].reshape(1,2,shape[1]).shape)
        result = np.vstack((result,arr[:,-shape[1]:].reshape(1,voices,shape[1])))
    return result

def weightsNorm(model):
    total_norm = 0
    for name,param in model.named_parameters():
        #print2File(name)
        if param.grad is not None:
            param_norm = param.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
    total_norm = total_norm ** (1. / 2)
    return total_norm
def savePlot(epocMetricsDictTrain, epocMetricsDictVal,filename):
                f = plt.figure(figsize=(40,60))
                ax1 = f.add_subplot(2,2,1)
                #ax1=plt.subplot(6,2,1)
                ax1.plot(np.array(epocMetricsDictTrain['loss']))
                ax1.set_xlabel('epocs')
                plt.title(' Train Data Loss ')
                plt.tight_layout()
                #plt.show()
                ax2=f.add_subplot(2,2,2)
                ax2.plot(np.array(epocMetricsDictTrain['acc']))
                ax2.set_xlabel('epocs')
                plt.title(' Train Data Acc ')
                plt.tight_layout()

                tempAxis = f.add_subplot(2,2,3)
                tempAxis.plot(np.array(epocMetricsDictVal['loss']))
                tempAxis.set_xlabel('epocs')
                plt.title('Valid Data Loss ')
                plt.tight_layout()

                tempAxis = f.add_subplot(2,2,4)
                tempAxis.plot(np.array(epocMetricsDictVal['acc']))
                tempAxis.set_xlabel('epocs')
                plt.title('Valid Data Acc ')
                plt.tight_layout()
                # f.set_figheight(15)
                # f.set_figwidth(15)
                f.savefig(filename)
                plt.cla()
                plt.close(f)
                plt.gcf().clear()

class VisdomLinePlotter(object):
    """Plots to Visdom"""
    def __init__(self, env_name='main'):
        self.viz = Visdom()
        self.env = env_name
        self.plots = {}
    def plot(self, var_name, split_name, title_name, x, y):
        if var_name not in self.plots:
            self.plots[var_name] = self.viz.line(X=np.array([x,x]), Y=np.array([y,y]), env=self.env, opts=dict(
                legend=[split_name],
                title=title_name,
                xlabel='Epochs',
                ylabel=var_name
            ))
        else:
            self.viz.line(X=np.array([x]), Y=np.array([y]), env=self.env, win=self.plots[var_name], name=split_name, update = 'append')

def getDevice():
    if torch.cuda.device_count() > 0:
        device = torch.device('cuda:0')
        if torch.cuda.device_count() > 1:
            device = torch.device('cuda:1')
    else:
        device = torch.device('cpu')
    return device
def loadVocabularies():
    currentPath = Path.cwd()
    with open(currentPath/"Dataset/Vocabularies/vocabMidiArticGlobal.voc", "rb") as f:
        vocabMidiArticGlobal = pickle.load(f)
    
    with open(currentPath/"Dataset/Vocabularies/vocabRhythmGlobal.voc", "rb") as f:
        vocabRhythmGlobal = pickle.load(f)
    return vocabMidiArticGlobal, vocabRhythmGlobal
def totalParams(model, criterion):
    params = list(model.parameters()) + list(criterion.parameters())
    total_params = sum(x.size()[0] * x.size()[1] if len(x.size()) > 1 else x.size()[0] for x in params if x.size())
    return total_params

def midi2Tensor(filename, vocabMidiArticGlobal, vocabRhythmGlobal):
    # Load Piece
    piece=converter.parse(filename)
    partList = []
    
    for maybePart in piece:
        if maybePart.__class__.__name__ == 'Part':
            noteList = []
            i=0
            for element in maybePart:
                print(element)
                if element.__class__.__name__ == 'TimeSignature':
                    timeSignature = TimeSignature(nom = element.beatCount, 
                                                  denom = int(4/element.beatDuration.quarterLength)
                                                  )
                    rhythmTemplate = RhythmTemplate(timeSignature)
                elif element.__class__.__name__ == 'Rest':
                    i += 1
                    print(i)
                    dur16 = int(4 * element.duration.quarterLength)
                    print(f"{dur16} Rest")
                    for cc in range(dur16):
                        noteList.append(Note2(fullName='rest', midi=0, 
                                                isFermata = 0,
                                                articulation = 1, 
                                                pitchClass = 12
                                                ))
                elif element.__class__.__name__ == 'Note':
                    #if element.duration.quarterLength != int(element.duration.quarterLength):
                    #    pepepe=34
                    dur16 = int(4 * element.duration.quarterLength)
                    #print(dur16)
                    if element.isRest:
                        print(f"{dur16} Rest")
                        for cc in range(dur16):
                            noteList.append(Note2(fullName='rest', midi=0, 
                                                    isFermata = 0,
                                                    articulation = 1, 
                                                    pitchClass = 12
                                                    ))
                    elif element.isNote:
                        print(f"{dur16} {element.pitch.nameWithOctave}")
                        if element.tie==None or element.tie.type=='start' : 
                            tempArtic = 1
                        else:
                            tempArtic = 0
                        noteList.append(Note2(fullName=element.pitch.nameWithOctave,
                                                midi=element.pitch.midi, 
                                                isFermata = 0,
                                                articulation = tempArtic,
                                                pitchClass = element.pitch.pitchClass,
                                                octave = element.pitch.octave
                                                ))
                        for cc in range(dur16-1):
                            noteList.append(Note2(fullName=element.pitch.nameWithOctave,
                                                midi=element.pitch.midi, 
                                                isFermata = 0,
                                                articulation = 0,
                                                pitchClass = element.pitch.pitchClass,
                                                octave = element.pitch.octave
                                                ))
            rhythmList = rhythmTemplate.getRhythmTokens(len(noteList),'last')
            tempPart = Part(noteList = noteList, instrument = None, metadata  =  None, 
                     timeSignature  =  timeSignature, rhythmList = rhythmList)  
            partList.append(part2Tensor(tempPart,vocabMidiArticGlobal, vocabRhythmGlobal))
            #tempPart = None
            #rhythmList = None
            #timeSignature = None
            #rhythmTemplate = None
    
            #[[1,2,3],[3,4,5]]
    return partList