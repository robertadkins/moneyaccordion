import cv2
import numpy as np
# Borrowed from https://github.com/benmel/point-to-define

hand_row_nw, hand_col_nw, hand_row_se, hand_col_se = [], [], [], []

def draw_rects(frame): 
    global hand_row_nw, hand_col_nw, hand_row_se, hand_col_se
    
    rows,cols,_ = frame.shape

    hand_row_nw = np.array([6*rows/20,6*rows/20,6*rows/20,10*rows/20,10*rows/20,10*rows/20,14*rows/20,14*rows/20,14*rows/20])

    hand_col_nw = np.array([9*cols/20,10*cols/20,11*cols/20,9*cols/20,10*cols/20,11*cols/20,9*cols/20,10*cols/20,11*cols/20])

    hand_row_se = hand_row_nw + 10
    hand_col_se = hand_col_nw + 10

    size = hand_row_nw.size
    for i in xrange(size):
        cv2.rectangle(frame,(hand_col_nw[i],hand_row_nw[i]),(hand_col_se[i],hand_row_se[i]),(0,255,0),1)
        black = np.zeros(frame.shape, dtype=frame.dtype)
        frame_final = np.vstack([black, frame])
    return frame_final

def get_hist(frame):
    global hand_row_nw, hand_col_nw, hand_row_se, hand_col_se
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    roi = np.zeros([90,10,3], dtype=hsv.dtype)

    size = hand_row_nw.size
    for i in xrange(size):
        roi[i*10:i*10+10,0:10] = hsv[hand_row_nw[i]:hand_row_nw[i]+10, hand_col_nw[i]:hand_col_nw[i]+10]

    hand_hist = cv2.calcHist([roi],[0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)
    
    return hand_hist

def hist_filter(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0,1], hist, [0,180,0,256], 1)
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
    cv2.filter2D(dst, -1, disc, dst)

    cv2.imshow("frame2", dst)

    ret, thresh = cv2.threshold(dst, 100, 255, 0)
    thresh = cv2.merge((thresh,thresh, thresh))

    cv2.GaussianBlur(dst, (3,3), 0, dst)

    return cv2.bitwise_and(frame, thresh)
