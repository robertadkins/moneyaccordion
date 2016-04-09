import numpy as np
import cv2
import moneydetector as md
import time


prev_frame = None

def diff_frames(frame):
    global prev_frame
    
    if prev_frame is None:
        prev_frame = frame

    diff = cv2.subtract(frame, prev_frame)

    #for later
    diff_mod = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    diff_mod = cv2.adaptiveThreshold(diff_mod, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 10)
    diff_mod = cv2.cvtColor(diff_mod, cv2.COLOR_GRAY2RGB)

    res = cv2.bitwise_and(frame, diff_mod)
    
    prev_frame = frame
    
    return res