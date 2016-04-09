import synthcontrol as sc
import time
import math

synth = sc.SynthControl()
j = 3
synth.play_note(j, 1)
for i in range(200):
    synth.adjust_mod((math.sin(i * (2 * math.pi) / 5) + 1)/2.0)
    if i <= 100:
        synth.adjust_cutoff(i / 100.0 * 0.8)
    time.sleep(0.1)
    if i % 5 == 0:
        j += 5
        synth.play_note(j, 1)

synth.note_off()
time.sleep(1)
synth.destroy()
