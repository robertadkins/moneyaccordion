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
    #diff_mod = cv2.morphologyEx(framet, cv2.MORPH_CLOSE, np.ones((2,2),np.uint8), iterations=10)
    #diff_mod = cv2.
    diff_mod = cv2.cvtColor(diff_mod, cv2.COLOR_GRAY2RGB)

    res = cv2.bitwise_and(frame, diff_mod)
    
    prev_frame = frame
    
    return res

def diff_frames_blurred(frame):
    global prev_frame
    
    if prev_frame is None:
        prev_frame = frame

    diff = cv2.subtract(frame, prev_frame)

    #for later
    diff_mod = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4,4))
    cv2.filter2D(diff_mod, -1, disc, diff_mod)

    ret, thresh = cv2.threshold(diff_mod, 100, 255, 0)
    thresh = cv2.merge((thresh,thresh, thresh))
    diff_mod = cv2.cvtColor(diff_mod, cv2.COLOR_GRAY2RGB)

    res = cv2.bitwise_and(frame, diff_mod)
    
    prev_frame = frame
    
    return res