import cv2
import moneydetector as md
import time
import hist_utils
import numpy as np
import camera
import math

#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

frames = []
frameCount = 0
maxFrames = 1

#this should be the camera
cap = cv2.VideoCapture(0)

trained_hand = False

pointing_threshold = 300

hand_hist = None

start_timer = 0
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

#while(False):
while(True):
    ret, frameorig = cap.read() #read a frame
    frameorig = cv2.flip(frameorig, 1)
    
    if not trained_hand:
        if cv2.waitKey(1) & 0xFF == ord('p'):
            hand_hist = hist_utils.get_hist(frameorig)
            trained_hand = True
            
        frame2 = hist_utils.draw_rects(frameorig, horizontal=False)
        cv2.imshow("frame", frame2)
    else:
        hist = hist_utils.hist_filter(frameorig, hand_hist)
        loc = hist_utils.get_color_point(frameorig, hand_hist)
        print loc
        cv2.circle(hist, (int(loc[0]),int(loc[1])), 5, [0,0,255], -1)
        cv2.imshow("frame", hist)
            

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
