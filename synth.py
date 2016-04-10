import numpy as np
import src.synthcontrol as sc
import math

class Synth:
    def __init__(self, screenSizeX, screenSizeY):
        self.STATE_SILENT = 0
        self.STATE_NOTE = 1
        self.STATE_CHORD = 2
        
        self.synth = sc.SynthControl()
        self.width = screenSizeX
        self.height = screenSizeY
        self.currNote = -1
        self.lastAspectRatio = 0
        self.state = self.STATE_SILENT
    
    def modSynth(self, hull, left_hand_open, right_hand_open):
        maxY = 0
        maxX = 0
        minY = 50000
        minX = 50000
        
        avgY = 0
        avgX = 0
        count = 0
        
        for pt in hull:
            x, y = pt[0][0], pt[0][1]
            avgY += y
            avgX += x
            count += 1
            if x > maxX:
                maxX = x
            elif x < maxX:
                minX = x
            if y > maxY:
                maxY = y
            elif y < minY:
                minY = y
        
        avgY = avgY / count
        avgX = avgX / count
        
        ar = (maxY - minY) / (maxX - minX)
        print "vol",math.atan(ar - self.lastAspectRatio) / math.pi / 2 + 1
        self.synth.adjust_vol(math.atan(ar - self.lastAspectRatio) / math.pi / 2 + 1)
        self.synth.adjust_cutoff(avgX / self.width * 0.2 + 0.8)
        self.lastAspectRatio = ar
        #self.calcNote(minY)
        self.calcNote(avgY, left_hand_open, right_hand_open)
        
        
    def calcNote(self, minY, left_hand_open, right_hand_open):
        section = 1.0 * (self.height - minY) / (self.height)
        print self.height, minY
        print "sec: ", section
        section = int ( math.floor(section * 4) )
        
        print "current section: ", section
        
        new_state = self.STATE_SILENT
        if not left_hand_open and not right_hand_open:
            new_state = self.STATE_CHORD
        elif not (left_hand_open and right_hand_open):
            new_state = self.STATE_NOTE
        
        if self.currNote != section or self.state != new_state:
            if(self.currNote != -1 or new_state == self.STATE_SILENT):
                self.synth.stop_sound()
            if new_state == self.STATE_CHORD:
                self.synth.play_chord(section, 1)
            if new_state == self.STATE_NOTE:
                self.synth.play_note(section, 1)
            self.currNote = section
    
    
    def cleanup(self):
        self.synth.destroy()
        
