import numpy as np
import cv2
import moneydetector as md
import time

#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

#this should be the camera
cap = cv2.VideoCapture(0)

#dollar_image = cv2.imread('7dollar.png', cv2.IMREAD_UNCHANGED)

#while(False):
while(True):
    ret, frame1 = cap.read() #read a frame
    #cv2.imshow('frame', frame) #display it

    #if you're checking for contours
    #md.detect(frame)

    time.sleep(.01)
    ret, frame2 = cap.read()

    diff = cv2.subtract(frame2, frame1)

    #for later
    #diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    #diff = cv2.adaptiveThreshold(diff, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 0)

    res = cv2.bitwise_and(frame2, diff)

    cv2.imshow("frame", diff)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.imshow('7dollar.png', dollar_image)
#md.detect(dollar_image)

cap.release()
cv2.destroyAllWindows()
