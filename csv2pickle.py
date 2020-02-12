# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:58:16 2019

@author: xribene
"""

from pandas import *
from pathlib import Path
import pandas as pd
import pickle
import numpy as np

# get only the columns you want from the csv file
df = pd.read_csv(Path.cwd()/'resources'/'base'/"MidiNotesList.csv")#, usecols=['Column Name1', 'Column Name2'])
df.where((pd.notnull(df)), None)
result = df.replace(pd.np.nan, None).to_dict(orient='records')


notesDictKeys = {}
for entry in result:
    if entry['Midi'] == entry['Midi'] :
        tempMidi = int(entry['Midi'])
        print(tempMidi)
        tempKeys = [column for column in entry.keys() if ((('minor' in column) or ('major' in column)) and int(entry[column]) == 0)]
        notesDictKeys[tempMidi] = {'primary' : {
                      'name' : entry['Note'],
                      'octave': int(entry['Octave']),
                      'acc': int(entry['Accidental']),
                      'cpc': int(entry['ChromPitchClass']),
                      'dpc': int(entry['DiatonicPitchClass']),
                      'treble': {'pos': float(entry['StaffPosTreble']), 'extraLine':  int(entry['ExtraLineTreble'])},
                      'bass': {'pos': float(entry['StaffPosBass']), 'extraLine':  int(entry['ExtraLineBass'])},
                      'keys' : tempKeys
                    }
        }
        if entry['Note.1'] == entry['Note.1']:
            tempKeys = [column for column in entry.keys() if ((('minor' in column) or ('major' in column)) and int(entry[column]) == 1)]
            notesDictKeys[tempMidi]['secondary'] =  {
                      'name' : entry['Note.1'],
                      'octave': int(entry['Octave.1']),
                      'acc': int(entry['Accidental.1']),
                      'cpc': int(entry['ChromPitchClass']),
                      'dpc': int(entry['DiatonicPitchClass.1']),
                      'treble': {'pos': float(entry['StaffPosTreble.1']), 'extraLine':  int(entry['ExtraLineTreble.1'])},
                      'bass': {'pos': float(entry['StaffPosBass.1']), 'extraLine':  int(entry['ExtraLineBass.1'])},
                      'keys' : tempKeys
                    }
        else:
            notesDictKeys[tempMidi]['secondary'] = None
        
# xls = ExcelFile('MidiNotesList.csv')
# df = xls.parse(xls.sheet_names[0])
# aaa = df.to_dict()
with open(Path.cwd()/'resources'/'base'/'notesPainterDict.pickle', 'wb') as handle:
    pickle.dump(notesDictKeys,handle)
#with open('notesPainterDict.pickle', 'rb') as handle:
#    notesDictNew = pickle.load(handle)


#with open(Path.cwd()/'resources'/'base'/'Vocabularies'/'globalVocabsDict.voc','rb') as f:
#    dicts = pickle.load(f)
    
#for midiInd in range(1,127):
#    aa = [result[i] for i in range(len(result)) if result[i]['Midi'] == float(midiInd)][0]
#    ee = notesDict[str(midiInd)]['primary']['treble']['pos'] == aa['StaffPosTreble']
#    if ee is False:
#        pass
#    ee = notesDict[str(midiInd)]['primary']['treble']['extraLine'] == aa['ExtraLineTreble']
#    if ee is False:
#        pass
#    ee =  notesDict[str(midiInd)]['primary']['bass']['pos'] == aa['StaffPosTreble']
#    if ee is False:
#        pass
#    ee =  notesDict[str(midiInd)]['primary']['bass']['extraLine'] == aa['ExtraLineBass']
#    if ee is False:
#        pass
#    
#    if notesDict[str(midiInd)]['secondary'] is not None:
#        ee =  notesDict[str(midiInd)]['secondary']['treble']['pos'] == aa['StaffPosTreble.1']
#        if ee is False:
#            pass
#        ee =  notesDict[str(midiInd)]['secondary']['treble']['extraLine'] == aa['ExtraLineTreble.1']
#        if ee is False:
#            pass
#        ee =  notesDict[str(midiInd)]['secondary']['bass']['pos'] == aa['StaffPosTreble.1']
#        if ee is False:
#            pass
#        ee =  notesDict[str(midiInd)]['secondary']['bass']['extraLine'] == aa['ExtraLineBass.1']
#        if ee is False:
#            pass
#        
