# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 05:02:10 2019

@author: xribene
"""
import itertools, copy
from operator import itemgetter
import numpy as np
class RhythmTemplate(object):
    def __init__(self,timeSignature):
        if not isinstance(timeSignature,str):
            inp = timeSignature.string
        else:
            inp = timeSignature
        if inp == '2/4':
            self.bar =  [1, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-2,-1,-2, 0,-2,-1,-2]
            self.accent=[0,-3,-2,-3,-1,-3,-2,-3]
        elif inp == '3/4':
            self.bar =  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-2,-1,-2, 0,-2,-1,-2, 0,-2,-1,-2]
            self.accent=[0,-3,-2,-3,-1,-3,-2,-3,-1,-3,-2,-3] 
        elif inp == '4/4':
            self.bar =  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-2,-1,-2, 0,-2,-1,-2, 0,-2,-1,-2, 0,-2,-1,-2]
            self.accent=[0,-3,-2,-3,-2,-4,-3,-4,-1,-3,-2,-3,-2,-4,-3,-4] 
        elif inp == '3/8':
            self.bar =  [1, 0, 0, 0, 0,-1]
            self.beat = [0,-1, 0,-1, 0,-1]
            self.accent=[0,-3,-2,-3,-2,-3] 
        elif inp == '4/8':
            self.bar =  [1, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-1, 0,-1, 0,-1, 0,-1]
            self.accent=[0,-3,-2,-3,-1,-3,-2,-3]  
        elif inp == '6/8':
            self.bar =  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1]
            self.accent=[0,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3]
        elif inp == '9/8':
            self.bar =  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1]
            self.accent=[0,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3]
        elif inp == '12/8':
            self.bar =  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1]
            self.beat = [0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1, 0,-1]
            self.accent=[0,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3,-1,-3,-2,-3,-2,-3]
        else:
            self.bar = None
            self.beat = None
            self.accent= None
            print(f"no info for timeSignature {inp}")
    def getRhythmTokens(self, dur,mode):
            if mode == 'first':
                return [str(self.bar[i%len(self.bar)])+'_'+ str(self.beat[i%len(self.bar)])+'_'+str(self.accent[i%len(self.bar)]) for i in range(-dur,0)]
            elif mode == 'last' or mode == 'between' :
                return [str(self.bar[i%len(self.bar)])+'_'+ str(self.beat[i%len(self.bar)])+'_'+str(self.accent[i%len(self.bar)]) for i in range(0,dur)]
            else:
                return None
class Vocabulary:
    def __init__(self, name):
        self.name = name
        self.token2index = {}
        self.token2count = {}
        self.index2token = {}
        self.n_tokens = 0 
      
    def index_tokens(self, tokenList):
        for token in tokenList:
            self.index_token(token)

    def index_token(self, token):
        if token not in self.token2index:
            self.token2index[token] = self.n_tokens
            self.token2count[token] = 1
            self.index2token[self.n_tokens] = token
            self.n_tokens += 1
        else:
            self.token2count[token] += 1
class Note(object):
    def __init__(self, fullName = None, midi = None, articulation = None, 
                 isFermata = None, isFirstInBar = None, pitchClass = None,
                 octave = None):
        #self.vocabulary  =  vocabulary
        self.midi  =  midi 
        self.articulation  =  articulation
        self.isFermata  =  isFermata
        self.isFirstInBar  =  isFirstInBar or []
        self.pitchClass  =  pitchClass
        self.octave  =  octave
        self.midiArtic  =  str(self.midi)+"_"+str(self.articulation)
        
class TimeSignature(object):
    def __init__(self, nom = None, denom = None, beats = None, accents = None):
        self.nom = nom
        self.denom = denom 
        self.beats = beats 
        self.accents = accents 
        self.duration16 = int(self.nom*16/self.denom)
        self.string = str(self.nom) + '/' + str(self.denom)
class Metadata(object):
    def __init__(self, title = None, pieceType = None, composer = None, 
                 period = None, source = None, uniqIndex = None,familyIndex=None,
                 key = None, transpose = None):
        self.title = title or []
        self.composer = composer or []
        self.pieceType = pieceType or []
        self.period = period or []
        self.source = source or []
        self.uniqIndex = uniqIndex
        self.familyIndex = familyIndex
        self.key = key or []
        self.transpose = transpose
    def returnAll(self):
      return(self.__dict__)
class Part(object):
    def __init__(self, noteList = None, instrument = None, metadata  =  None, 
                 timeSignature  =  None, rhythmList = None, keyList = None):
        self.metadata  =  metadata or []
        self.timeSignature  =  timeSignature or []
        self.noteList  =  noteList or []
        self.rhythmList = rhythmList or []
        self.instrument  =  instrument or []
        self.keyList = keyList or []
    def getSize(self):
        return len(self.noteList)
    def getRhythmList(self,mode, vocabulary = None):
        if mode == 'rhyrhm':
            return self.rhythmList
        elif mode == 'rhythmIndex':
            return [vocabulary.token2index[rhythm] for rhythm in self.rhythmList]
    def getKeyList(self,mode, vocabulary = None):
        if mode == 'key':
            return self.keyList
        elif mode == 'keyIndex':
            return [vocabulary.token2index[key] for key in self.keyList]
    def getNoteList(self, mode, vocabulary = None):
        #print(voc)
        if mode == 'midi':
            return [note.midi for note in self.noteList]
        elif mode == 'pitchClass':
            return [note.pitchClass for note in self.noteList]
        elif mode == 'articulation':
            return [note.articulation for note in self.noteList]
        elif mode == 'midiArtic' :
            return [note.midiArtic for note in self.noteList]
        elif mode == 'indexMidiArtic' :
            return [vocabulary.token2index[note.midiArtic] for note in self.noteList]
class Duet(object):
    def __init__(self, metadata = None, timeSignature = None, parts = None):
        self.parts = parts or []
        self.metadata = metadata or []
        self.timeSignature = timeSignature or []
        self.part1 = self.parts[0]
        self.part2 = self.parts[1]
    def checkValid(self):
        if len(self.part1.noteList) != len(self.part2.noteList):
            print(f'size missmatch {self.metadata.__dict__}')
            print(len(self.part1.noteList))
            print(len(self.part2.noteList))
            raise
        elif len(self.part1.rhythmList) != len(self.part2.rhythmList):
            print(f'size missmatch Rhythms {self.metadata.__dict__}')
            print(len(self.part1.rhythmList))
            print(len(self.part2.rhythmList))
            raise
        elif len(self.part1.rhythmList) != len(self.part2.noteList):
            print(f'size missmatch Rhythm-Note{self.metadata.__dict__}')
            print(len(self.part1.rhythmList))
            print(len(self.part2.noteList))
            print(self.timeSignature.__dict__)
            raise
        else:
            return 1
class Trio(object):
    def __init__(self, metadata = None, timeSignature = None, parts = None, bassPart = None):
        self.parts = parts or []
        self.metadata = metadata or []
        self.timeSignature = timeSignature or []
        self.part1 = self.parts[0]
        self.part2 = self.parts[1]
        self.part3 = bassPart
    def checkValid(self):
        if len(self.part1.noteList) != len(self.part2.noteList):
            print(f'size missmatch {self.metadata.__dict__}')
            print(len(self.part1.noteList))
            print(len(self.part2.noteList))
            raise
        elif len(self.part1.noteList) != len(self.part3.noteList):
            print(f'size missmatch {self.metadata.__dict__}')
            print(len(self.part1.noteList))
            print(len(self.part3.noteList))
            raise
        elif len(self.part1.rhythmList) != len(self.part2.rhythmList):
            print(f'size missmatch Rhythms {self.metadata.__dict__}')
            print(len(self.part1.rhythmList))
            print(len(self.part2.rhythmList))
            raise
        elif len(self.part1.rhythmList) != len(self.part2.noteList):
            print(f'size missmatch Rhythm-Note{self.metadata.__dict__}')
            print(len(self.part1.rhythmList))
            print(len(self.part2.noteList))
            raise
        else:
            return 1
class Piece(object):
    def __init__(self, metadata = None, timeSignature = None, parts = None, transpose = 0):
        self.parts = parts or []
        self.metadata = metadata or []
        self.timeSignature = timeSignature or []
        self.rhythmList = self.parts[0].rhythmList
        self.transpose = transpose
    def getDuets(self, voices = [0,1,2,3]):
        permuts=list(itertools.permutations(voices,2))
        duets = [] #list of Duet
        for perm in permuts:
            #print(self.parts)
            temp= Duet(metadata=self.metadata, parts=itemgetter(*perm)(self.parts),
                       timeSignature=self.timeSignature)
                    
            temp.checkValid()
            duets.append(temp)
        return duets
    def getTrios(self, voices=[0,1,2], cond = 3):
        permuts=list(itertools.permutations(voices,2))
        trios = [] #list of Duet
        for perm in permuts:
            #print(self.parts)
            temp = Trio(metadata=self.metadata, parts=itemgetter(*perm)(self.parts),
                       bassPart = self.parts[3], timeSignature=self.timeSignature)
            temp.checkValid()
            trios.append(temp)
        return trios
