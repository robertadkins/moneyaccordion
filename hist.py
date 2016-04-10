import cv2
import moneydetector as md
import time
import hist_utils
import numpy as np
import camera
from synth import Synth
import math
import os.path

#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

frames = []
frameCount = 0
maxFrames = 1

#this should be the camera
cap = cv2.VideoCapture(0)

fgbg = cv2.BackgroundSubtractorMOG()

trained_hand = False
trained_dollar = True

pointing_threshold = 50

hand_hist = None
dollar_hist = None

ret, frame1 = cap.read()
syn = Synth(len(frame1), len(frame1[0]))

start_timer = 0
cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

frame_num = 0
frame_len = 10

def addKeyboard(img):
    xlen = len(img[0])
    ylen = len(img)

    note = syn.NUM_NOTES - syn.currNote - 1

    cv2.rectangle(img,(0,0),(xlen,ylen),(0,255,0),3)

    noteboxy = ylen / syn.NUM_NOTES
    noteboxx = xlen / syn.NUM_NOTES

    for i in range(syn.NUM_NOTES + 1):
        cv2.rectangle(img,(0, noteboxy * i), (xlen, noteboxy*(i+1)), (0,255,0), 2)
        
    cv2.rectangle(img,(0, noteboxy * note), (xlen, noteboxy*(note+1)), (0,0,255), 6)
    cv2.rectangle(img,(xlen-50, noteboxy*note+20), (xlen-10, noteboxy*(note+1)-20), (0,0,255), -1)


while(True):
    ret, frameorig = cap.read() #read a frame
    frameorig = cv2.flip(frameorig, 1)

    if os.path.isfile("hand_hist.npy") and not trained_hand:
        # read pipe cleaner histogram from file
        hand_hist = np.load("hand_hist.npy")
        trained_hand = True
        frame2 = hist_utils.draw_rects(frameorig, horizontal=False)
        cv2.imshow("frame", frame2)
    elif not trained_hand:
        # train pipe cleaner
        if cv2.waitKey(1) & 0xFF == ord('p'):
            hand_hist = hist_utils.get_hist(frameorig)
            np.save("hand_hist", hand_hist)
            trained_hand = True

        frame2 = hist_utils.draw_rects(frameorig, horizontal=False)
        cv2.imshow("frame", frame2)
    else:
        ### PUT THRESHOLD HERE
        gray = cv2.cvtColor(frameorig, cv2.COLOR_BGR2GRAY)
	
	greenLower = (20, 10, 20)
	greenUpper = (65, 255, 255) # 35, 19, 58
	
	hsv = cv2.cvtColor(frameorig, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	mask = cv2.bitwise_and(gray, mask)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,\
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
	if len(cnts) > 0:
            maxcnt = None
            maxarea = 0
            for cnt in cnts:
                newarea = cv2.contourArea(cnt)
                if newarea > maxarea:
                    maxarea = newarea
                    maxcnt = cnt
            hull = cv2.convexHull(maxcnt)
            
            if frame_num % frame_len == 0:
                cv2.drawContours(frameorig, [hull], 0, (150,50,0), 3)

            M = cv2.moments(maxcnt)
            mean = [0,0]
            mean[0] = int(M['m10']/M['m00'])
            mean[1] = int(M['m01']/M['m00'])
                
            left = frameorig[:,0:mean[0]]
            dist_left = 0
            if len(left) != 0:
                for i in range(len(left)):
                    frameorig[i, mean[0], 0] = 255
                farthest_point_left = hist_utils.get_color_point(left, hand_hist)
                  
            right = frameorig[:,mean[0]:]
            dist_right = 0
            if len(right) != 0:
                farthest_point_right = hist_utils.get_color_point(right, hand_hist)
                
            if frame_num % frame_len == 0:
                cv2.circle(frameorig, (mean[0], mean[1]), 5, [255,0,255], -1)
            
            left_open = True if farthest_point_left is None else farthest_point_left[1] < mean[1] - pointing_threshold
            right_open = True if farthest_point_right is None else farthest_point_right[1] < mean[1] - pointing_threshold

            if farthest_point_right is not None:
                farthest_point_right = (farthest_point_right[0] + mean[0], farthest_point_right[1])
                cl = [0,255,0] if not right_open else [0,255,255]
                if frame_num % frame_len == 0:
                    cv2.circle(frameorig, (int(farthest_point_right[0]),int(farthest_point_right[1])), 5, cl, -1)
            if farthest_point_left is not None:
                cl = [0,255,0] if not left_open else [0,0,255]
                if frame_num % frame_len == 0:
                    cv2.circle(frameorig, (int(farthest_point_left[0]),int(farthest_point_left[1])), 5, cl, -1)
                print "left open: ",left_open
                print "left: ", farthest_point_left[1]
                print "mean: ", mean[1]
                print "th: ", mean[1] - pointing_threshold
            syn.modSynth(hull, left_open, right_open)
                           
        addKeyboard(frameorig)

        if frame_num % frame_len == 0:
            cv2.imshow("frame", frameorig)
            frame_num = 0
            
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

syn.cleanup()

cap.release()
cv2.destroyAllWindows()
