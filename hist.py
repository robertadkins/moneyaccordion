import numpy as npA
import cv2
import moneydetector as md
import time
import hist_utils
import numpy as np
import camera
from synth import Synth
import math

#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

frames = []
frameCount = 0
maxFrames = 1

#this should be the camera
cap = cv2.VideoCapture(0)

fgbg = cv2.BackgroundSubtractorMOG()

#dollar_image = cv2.imread('7dollar.png', cv2.IMREAD_UNCHANGED)

trained_hand = False
trained_dollar = False

hand_hist = None
dollar_hist = None

ret, frame1 = cap.read()
syn = Synth(len(frame1), len(frame1[0]))

start_timer = 0
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.namedWindow('edge', cv2.WINDOW_NORMAL)

def addKeyboard(img):
    xlen = len(img[0])
    ylen = len(img)

    note = 4 - syn.currNote - 1

    cv2.rectangle(img,(0,0),(xlen,ylen),(0,255,0),3)

    noteboxy = ylen / 3
    noteboxx = xlen / 3

    cv2.rectangle(img,(0, noteboxy), (xlen, noteboxy*2), (0,255,0), 2)
    cv2.rectangle(img,(0, noteboxy*2), (xlen, noteboxy*3), (0,255,0), 2)
    cv2.rectangle(img,(0, noteboxy*3), (xlen, ylen), (0,255,0), 2)
    cv2.rectangle(img,(xlen-50, noteboxy*note+20), (xlen-10, noteboxy*(note+1)-20), (0,255,0), -1)


#while(False):
while(True):
    ret, frameorig = cap.read() #read a frame
    grayframe = cv2.cvtColor(frameorig, cv2.COLOR_BGR2GRAY)
    frameorig = cv2.flip(frameorig, 1)
    edge = cv2.Canny(grayframe, 100, 200)

    mask = fgbg.apply(frameorig)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    frame1 = cv2.bitwise_and(frameorig, mask)
    frame1 = frameorig

    if not trained_hand:
        if cv2.waitKey(1) & 0xFF == ord('p'):
            hand_hist = hist_utils.get_hist(frameorig)
            trained_hand = True

        frame2 = hist_utils.draw_rects(frameorig, horizontal=False)
        cv2.imshow("frame", frame2)

    elif not trained_dollar:
        start_timer += 1
        if cv2.waitKey(1) & 0xFF == ord('p'):# or start_timer == 100:
            dollar_hist = hist_utils.get_hist(frameorig)
            trained_dollar = True

        frame2 = hist_utils.draw_rects(frameorig)
        cv2.imshow("frame", frame2)
    else:
        hist = hist_utils.hist_filter(frameorig, dollar_hist)
        grayhist = cv2.cvtColor(hist, cv2.COLOR_BGR2GRAY)

        combined = cv2.bitwise_and(edge, grayhist)
        cv2.imshow("edge", edge)

        diffframe1 = camera.diff_frames_blurred(frame1)
        frame1 = hist_utils.hist_filter(diffframe1, dollar_hist)

        # calculate average frame over maxFrames

        if len(frames) < maxFrames:
            frames.append(frame1)
        else:
            frames[frameCount % maxFrames] = frame1
        frameCount += 1

        summedFrame = np.zeros((len(frame1),len(frame1[0]),3))
        for f in frames:
            cv2.accumulate(f, summedFrame)

        summedFrame /= len(frames)
        summedFrame = summedFrame.astype("uint8")

        frame2 = cv2.cvtColor(summedFrame, cv2.COLOR_BGR2GRAY)

        ret, framet = cv2.threshold(frame2, 100, 255, 0)
        framet = cv2.morphologyEx(framet, cv2.MORPH_CLOSE, np.ones((2,2),np.uint8), iterations=10)
        framet1 = np.copy(framet)
        #_,contours,hierarchy = cv2.findContours(framet, 1, 2)
        contours, hierarchy = cv2.findContours(framet, 1, 2)


        framet = cv2.cvtColor(framet, cv2.COLOR_GRAY2RGB)
        allpts = []
        if len(contours) > 0:
            #print contours
            print len(contours)

            mean = [0,0]
            # assumption: each contour is tiny
            for cnt in contours:
                # print cnt
                mean[0] += cnt[0][0][0]
                mean[1] += cnt[0][0][1]
            mean[0] /= len(contours)
            mean[1] /= len(contours)

            stddev = 0
            for cnt in contours:
                stddev += (cnt[0][0][0] - mean[0]) * (cnt[0][0][0] - mean[0])
                stddev += (cnt[0][0][1] - mean[1]) * (cnt[0][0][1] - mean[1])
            stddev /= len(contours)
            stddev = math.sqrt(stddev)

            for cnt in contours:
                #print cnt.tolist()
                if math.sqrt((cnt[0][0][0] - mean[0]) * (cnt[0][0][0] - mean[0]) + (cnt[0][0][1] - mean[1]) * (cnt[0][0][1] - mean[1])) < stddev:
                    allpts = allpts + cnt.tolist()
                    cv2.drawContours(summedFrame, cnt, -1, (255,0,0), 3)

            #print allpts
            if len(allpts) > 0:
                hull = cv2.convexHull(np.array(allpts))
                cv2.drawContours(summedFrame, [hull], -1, (0,255,0), 3)
                syn.modSynth(hull)


                  #framet = cv2.cvtColor(framet, cv2.COLOR_GRAY2RGB)
                  #framet[1] = framet1
        farthest_point, hand_isolated_frame = hist_utils.find_hand_farthest_point(frameorig, hand_hist)
        if farthest_point is not None:
            cv2.circle(summedFrame, farthest_point, 5, [0,0,255], -1)

        addKeyboard(summedFrame)

        cv2.imshow("frame", summedFrame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#cv2.imshow('7dollar.png', dollar_image)
#md.detect(dollar_image)

syn.cleanup()

cap.release()
cv2.destroyAllWindows()
