<!-- # ![BachDuet](https://github.com/xribene/BachDuet/blob/master/resources/base/Images/bachDuetSplashYellow1024.png?raw=true ) -->
<img src="https://github.com/xribene/BachDuet/blob/master/resources/base/Images/bachDuetSplashYellow1024.png?raw=true" width="40%">

# BachDuet
<table>
<tr>
<td>
  BachDuet enables a human performer to improvise a duet counterpoint with a computer agent in real time. 
</td>
</tr>
</table>


## Links
Webpage / Demos :  http://www2.ece.rochester.edu/projects/air/projects/BachDuet.html

Paper : https://www.nime.org/proceedings/2020/nime2020_paper125.pdf



## Usage
### Requirements
#### Hardware
- Midi Keyboard (if not available, you can still use your pc keyboard)
#### Software
- Any virtual midi synthesizer. BachDuet's output is MIDI events and not audio, so you need a synthesizer. it can be a standalone synth like Fluidsynth, OMNI midi, or it can be any DAW. 
#### Libraries/OS
- Tested in Windows and Mac / it should work on Linux also
- Python 3.8
- PyQt5
- pytorch > 1.4
- python-rtmidi
- pyqtgraph
- music21
- numpy
- scipy
- matplotlib
#### Steps
- python main.py
- Choose HumanVsMachine, and enter your name
- Press Ctrl+P (or the settings icon) to open settings and select Midi input and output
- Press space (or the play icon) to start (or pause)


## Bugs
### Major
- Due to a change in the latest version of pyqt5, the pianoroll visualization doesn't work. https://github.com/pyqtgraph/pyqtgraph/issues/1057.
### Minor
- Fix the "MachineVsMachine" mode.

## TODO
- Clean library depedencies
- Clean and add documentation the remaining code
- Embed a synthesizer using the FluidSynth API for python