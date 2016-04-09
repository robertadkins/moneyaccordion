import numpy as np
import cv2
import moneydetector as md
import time
import hist_utils
import numpy as np


#HEY HEY Maybe we should look into tracking fingers holding the bill rather than the bill itself
#easier to measure velocity, can't really measure bend in the dollar
#plus, finger overlap on the dollar inhibits the ability to recognize the dollar contour

#this should be the camera
cap = cv2.VideoCapture(0)

#dollar_image = cv2.imread('7dollar.png', cv2.IMREAD_UNCHANGED)

trained_dollar = False

dollar_hist = None

#while(False):
while(True):
    ret, frame1 = cap.read() #read a frame
    
    frame1 = cv2.flip(frame1, 1)
    
    if not trained_dollar:
        if cv2.waitKey(1) == ord('p') & 0xFF:
            dollar_hist = hist_utils.get_hist(frame1)
            trained_dollar = True
            
        frame1 = hist_utils.draw_rects(frame1)

    else:
        hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0,1], dollar_hist, [0,180,0,256], 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
        cv2.filter2D(dst, -1, disc, dst)

        ret, thresh = cv2.threshold(dst, 100, 255, 0)
        thresh = cv2.merge((thresh,thresh, thresh))

        cv2.GaussianBlur(dst, (3,3), 0, dst)

        frame1 = cv2.bitwise_and(frame1, thresh)
        
    cv2.imshow("frame", frame1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.imshow('7dollar.png', dollar_image)
#md.detect(dollar_image)

cap.release()
cv2.destroyAllWindows()
