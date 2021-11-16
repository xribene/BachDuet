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
        seed = None
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

        self.keyEvents = ['72_1', '72_0','74_1', '74_0']*4
        self.store = {
            'hiddenStates' : [],
            'logits' : [],
            'midiArtic' : [],
            'seed' : seed,
            'type' : 'zero'
        }
        self.store['hiddenStates'].append(self.neuralNet.hiddenMidi)
        # print(torch.sum(self.neuralNet.hiddenMidi[1]))
        self.runTest()

    def runTest(self):

        for i in range(16):
            
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
            self.store['hiddenStates'].append(self.neuralNet.hiddenMidi)
            self.store['logits'].append(pred['logits'])
            self.store['midiArtic'].append(f"{pred['midi']}_{pred['artic']}")

            # print(list(self.outputQueue.queue))
            # print(currentTrigger)
        with open(f"bachDuetTest_rand.dict", 'wb') as f :
            pickle.dump(self.store, f)
        print([torch.mean(x) for x in self.store['logits']])
        print([x for x in self.store['midiArtic']])

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