import numpy as np
import cv2
import moneydetector as md
import time
import hist_utils
import numpy as np
import camera

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
        frame1 = camera.diff_frames(frame1)
        frame1 = hist_utils.hist_filter(frame1, dollar_hist)
        
        
    cv2.imshow("frame", frame1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.imshow('7dollar.png', dollar_image)
#md.detect(dollar_image)

cap.release()
cv2.destroyAllWindows()