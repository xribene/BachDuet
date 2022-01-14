from GuiClasses.NeuralNetworkIsmir import NeuralNet
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from queue import Queue
from utils import Params
import pickle
import numpy as np
from GuiClasses.Player import *
from GuiClasses.Timers import Clock
import torch 

class ApplicationContext(object):
    """
    Manages the resources. There is not
    actual need for this Class. The only reason
    to use it is for compatibility with the fbs
    library, in order to create an exe file for the app

    Methods
    -------
    get_resource(name) : str
        returns the path of a resource by name
    """
    def __init__(self):
        self.path = Path.cwd() / 'resources' / 'base'
    def get_resource(self, name):
        return str(self.path / name)

class BachDuet(QWidget):

    def __init__(self, appctxt, logger, parent = None):
        super(BachDuet, self).__init__()
        self.setObjectName("BachDuet")
        # self.config contains system settings loaded from 
        # a json file using the Params() class from utils.py
        self.config = Params(appctxt.get_resource("bachDuet.json"))
        self.cwd = Path.cwd()
        self.storagePath = self.cwd / self.config.storagePath
        self.appctxt = appctxt
        self.ctrlPressed = False
        self.params = self.config.default
        seed = 11
        # notesPainterDict is used for displaying the notes on the Staves,
        # and it contains all the information about each notes position in the Staff
        # as well as their spellin given different key configurations.
        with open(self.appctxt.get_resource('notesPainterDict.pickle'), 'rb') as handle:
            self.notesDict = pickle.load(handle)

        self.player1 = Player( name = 'testNeuralNet', type = 'machine',
                               params = self.params, realTimeInput = True, 
                               inputType = 'midi', modules = {}, 
                               holdFlag = False)
        self.player1.temperature = 0.00000001
        self.outputQueue = Queue()
        self.clock = Clock(self.appctxt)
        self.neuralNet = NeuralNet(self.outputQueue, 
                        self.notesDict, self.appctxt, 
                        parentPlayer = self.player1, parent = self, seed=seed)

        self.midis = [72,72,74,74]*4
        self.artics = [1,0,1,0]*4
        self.keyEvents = [str(self.midis[i])+'_'+str(self.artics[i]) for i in range(len(self.midis))]
        self.store = {
            'hiddenStates' : [],
            'logits' : [],
            'softmax' : [],
            'aiMidiArtic' : [],
            'seed' : seed,
            'type' : 'zero',
            'keyEvents' : self.keyEvents,
            'tick' : [],
            'rhythmToken' : [],
            "temperature" : self.player1.temperature

        }
        self.store['hiddenStates'].append([self.neuralNet.hiddenMidi[0].numpy(), self.neuralNet.hiddenMidi[1].numpy()])
        # print(torch.sum(self.neuralNet.hiddenMidi[1]))
        self.runTest()

    def runTest(self):

        for i in range(len(self.keyEvents)):
            
            currentTrigger = self.clock.singleRun()

            humanInp = {
                'midi' : int(self.keyEvents[i].split('_')[0]),
                'artic' : int(self.keyEvents[i].split('_')[1]),
                'tick' : int(currentTrigger['tick']),
                'rhythmToken' : currentTrigger['rhythmToken'],
                'globalTick' : currentTrigger['globalTick']
            }
            
            self.neuralNet.forwardPass(humanInp)
            pred = self.outputQueue.get()
            # print(torch.mean(pred['logits']))

            # print(pred.keys())
            self.store['hiddenStates'].append([self.neuralNet.hiddenMidi[0].numpy(), self.neuralNet.hiddenMidi[1].numpy()])
            self.store['logits'].append(pred['logits'].numpy())
            self.store['softmax'].append(pred['softmax'].numpy())
            self.store['aiMidiArtic'].append(f"{pred['midi']}_{pred['artic']}")
            self.store['rhythmToken'].append(currentTrigger['rhythmToken'])
            self.store['tick'].append(int(currentTrigger['tick']))

            # print(list(self.outputQueue.queue))
            # print(currentTrigger)
        self.store['rhythmInd'] = [self.neuralNet.vocabRhythmGlobal.token2index[x] for x in self.store['rhythmToken']]
        self.store['aiMidiArticInd'] = [self.neuralNet.vocabMidiArticGlobal.token2index[x] for x in self.store['aiMidiArtic']]
        self.store['humanMidiArticInd'] = [self.neuralNet.vocabMidiArticGlobal.token2index[x] for x in self.store['keyEvents']]
        self.store['humanMidiArtic'] = [x for x in self.store['keyEvents']]
        self.store['humanCpc'] = [int(self.neuralNet.notesDict[x]['primary']['cpc']) if x!=0 else 12 for x in self.midis]

        self.store['humanMidi'] = self.midis
        self.store['aiMidi'] = [int(x.split("_")[0]) for x in self.store["aiMidiArtic"]]
        self.store['aiCpc'] = [int(self.neuralNet.notesDict[x]['primary']['cpc']) if x!=0 else 12 for x in self.store['aiMidi']]


        # with open(f"/home/xribene/Projects/BachDuet-WebGUI/public/bachDuetTest.dict", 'wb') as f :
        #     pickle.dump(self.store, f)
        np.save(f"/home/xribene/Projects/BachDuet-WebGUI/public/bachDuetTest.npy", self.store)
        print([np.mean(x) for x in self.store['logits']])
        print([x for x in self.store['humanMidiArtic']])
        print([x for x in self.store['humanMidiArticInd']])
        print([x for x in self.store['aiMidiArtic']])
        print([x for x in self.store['aiMidiArticInd']])
        print([x for x in self.store['aiMidi']])
        print([x for x in self.store['aiCpc']])
        # print([x for x in self.store['rhythmToken']])
        # print([x for x in self.store['rhythmInd']])
        # print([x for x in self.store['humanCpc']])
        for i in range(17):
            print([np.mean(x) for x in self.store['hiddenStates'][i][0]])
            print([np.mean(x) for x in self.store['hiddenStates'][i][1]])
            # print([np.mean(x) for x in self.store['hiddenStates'][1][0]])
            # print([np.mean(x) for x in self.store['hiddenStates'][1][1]])
            # print([np.mean(x) for x in self.store['hiddenStates'][2][0]])
            # print([np.mean(x) for x in self.store['hiddenStates'][2][1]])


if __name__ == '__main__':
    logger = None # configure_logger('default')
    import sys
    CUDA_LAUNCH_BLOCKING=1
    appctxt = ApplicationContext()
    
    styleSheet = appctxt.get_resource("styleSheet.css")
    app = QApplication(sys.argv)
    
    # with open(styleSheet,"r") as fh:
    #     app.setStyleSheet(fh.read())

    bachDuet = BachDuet(appctxt, logger)

    # exit_code = app.exec_()   
    # sys.exit(exit_code)