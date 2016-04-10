import numpy as np
import src.synthcontrol as sc
import math

class Synth:
    def __init__(self, screenSizeX, screenSizeY):
        self.synth = sc.SynthControl()
        self.width = screenSizeX
        self.height = screenSizeY
        self.currNote = -1
        self.lastAspectRatio = 0
    
    def modSynth(self, hull):
        maxY = 0
        maxX = 0
        minY = 50000
        minX = 50000
        
        avgY = 0
        count = 0
        
        for pt in hull:
            x, y = pt[0][0], pt[0][1]
            avgY += y
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
        
        ar = (maxY - minY) / (maxX - minX)
        print "vol",math.atan(ar - self.lastAspectRatio) / math.pi / 2 + 1
        self.synth.adjust_vol(math.atan(ar - self.lastAspectRatio) / math.pi / 2 + 1)
        self.lastAspectRatio = ar
        #self.calcNote(minY)
        self.calcNote(avgY)
        
        
    def calcNote(self, minY):
        section = 1.0 * (self.height - minY) / (self.height / 3)
        print self.height, minY
        print "sec: ", section
        section = int ( math.floor(section * 8) )
        
        print "current section: ", section 
        
        if self.currNote != section:
            if(self.currNote != -1):
                self.synth.note_off()
            self.synth.play_note(section, 1)
            self.currNote = section
    
    
    def cleanup(self):
        self.synth.destroy()
        