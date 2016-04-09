import numpy as np
import cv2
import moneydetector as md

#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

#this should be the camera
cap = cv2.VideoCapture(0)

#dollar_image = cv2.imread('7dollar.png', cv2.IMREAD_UNCHANGED)

#while(False):
while(True):
    ret, frame = cap.read() #read a frame
    cv2.imshow('frame', frame) #display it

    md.detect(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.imshow('7dollar.png', dollar_image)
#md.detect(dollar_image)

cap.release()
cv2.destroyAllWindows()
