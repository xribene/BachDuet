from pathlib import Path
import torch
import torch.nn as nn
import pickle
from music21 import *
import numpy as np
from utils import TensorBuffer
from ParsingClasses import Part, TimeSignature, Duet, Piece, RhythmTemplate
from ParsingClasses import Note as Note2

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








partsTensorList =  midi2Tensor(filename, vocabDict['midiArtic'], vocabDict['rhythm'])
