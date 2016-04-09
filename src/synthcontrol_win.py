################################################################################
# This file provides an interface to send notes / parameter changes to a synth
################################################################################

import rtmidi as rt
from subprocess import Popen
import time

class SynthControl:
    """ interfaces via MIDI to a synthesizer """
    SCALES = [[0, 2, 4, 5, 7, 9, 11, 12],\
              [0, 2, 3, 5, 7, 8, 10, 12]] # major / minor
    #helm
    #scale
    #cutoff
    #mod
    
    def __init__(self, key='C', major=True):
        base = ord(key.upper()) - ord('C') + 60
        if major:
            scale = self.SCALES[0]
        else:
            scale = self.SCALES[1]
        self.scale = map(lambda x: x + base, scale)
        self.note = -1

        # launch helm
        self.helm = Popen("C:\Program Files\Helm\Helm.exe", shell=True)
        time.sleep(1)

        self.midiout = rt.MidiOut()
        ports = self.midiout.get_ports()
        print ports
        self.midiout.open_port(2)

    def train(self):
        """ use this to train parameters for MIDI communication """
        raw_input("Press enter to train cutoff ")
        self.adjust_cutoff(0.8)

        raw_input("Press enter to train mod ")
        self.adjust_mod(0)
        
        raw_input("Press enter to train volume ")
        self.adjust_vol(0.8)
        
        
    def destroy(self):
        self.helm.terminate()
    
    def play_note(self, num, velocity):
        """ num is an index for the scale, velocity is a float between 0 and 1 """
        if self.note != -1:
            self.note_off()
            
        self.note = self.scale[num % len(self.scale)]
        self.midiout.send_message([0x90, self.note, int(velocity * 127)])

    def note_off(self):
        self.midiout.send_message([0x80, self.note, 0])
        self.note = -1

    def adjust_cutoff(self, val):
        """ val is between 0 and 1 """
        self.midiout.send_message([0xB0, 0, int(val * 127)])

    def adjust_mod(self, val):
        """ val is between 0 and 1 """
        self.midiout.send_message([0xB0, 1, int(val * 127)])

    def adjust_vol(self, val):
        self.midiout.send_message([0xB0, 2, int(val * 127)])
