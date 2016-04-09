import numpy as np
import src.synthcontrol as sc

class Synth:
    def __init__(self, screenSizeX, screenSizeY):
        self.synth = sc.SynthControl()
        self.width = screenSizeX
        self.height = screenSizeY
        self.currNote = -1
    
    def modSynth(self, hull):
        maxY = 0
        maxX = 0
        minY = 50000
        minX = 50000
        for (x,y) in hull:
            if x > maxX:
                maxX = x
            elif x < maxX:
                minX = x
            if y > maxY:
                maxY = y
            elif y < minY:
                minY = y
        
        ar = (maxY - minY) / (maxX - minX)
        calcNote(self, maxY)
        
        
        
    def calcNote(self, maxY):
        section = maxY / self.height * 1.0
        section = (section * 8).truncate()
        
        if self.currNote != section:
            self.playNote(synth, section, 1)
            self.currNote = section
    
    
        
        