import cv2
import numpy as np
# Borrowed from https://github.com/benmel/point-to-define

hand_row_nw, hand_col_nw, hand_row_se, hand_col_se = [], [], [], []

def draw_rects(frame, horizontal = True): 
    global hand_row_nw, hand_col_nw, hand_row_se, hand_col_se
    
    rows,cols,_ = frame.shape

    
    if horizontal:
        hand_row_nw = np.array([9*rows/20,10*rows/20,11*rows/20,9*rows/20,10*rows/20,11*rows/20,9*rows/20,10*rows/20,11*rows/20])

        hand_col_nw = np.array([6*cols/20,6*cols/20,6*cols/20,10*cols/20,10*cols/20,10*cols/20,14*cols/20,14*cols/20,14*cols/20])
    else:
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

    # cv2.imshow("frame2", dst)

    ret, thresh = cv2.threshold(dst, 100, 255, 0)
    thresh = cv2.merge((thresh,thresh, thresh))

    cv2.GaussianBlur(dst, (3,3), 0, dst)

    return cv2.bitwise_and(frame, thresh)

def find_hand_farthest_point(frame, hist):
    hand_isolated_frame = hist_filter(frame, hand_hist)
    
    gray = cv2.cvtColor(hand_isolated_frame, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(gray, 0, 255, 0)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours is not None and len(contours) > 0:
        max_i = 0
        max_area = 0

        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                max_i = i

        largest_contour = contours[max_i]
        
        
        hull = cv2.convexHull(largest_contour)
        
        moments = cv2.moments(contour)
        centroid = None
        if moments['m00'] != 0:
            cx = int(moments['m10']/moments['m00'])
            cy = int(moments['m01']/moments['m00'])
            centroid = (cx,cy)
        
        defects = None
        non_returnpoints_hull = cv2.convexHull(contour, returnPoints=False)
        if non_returnpoints_hull is not None and len(non_returnpoints_hull) > 3 and len(contour) > 3:
            defects = cv2.convexityDefects(contour, non_returnpoints_hull)

        if centroid is not None and defects is not None and len(defects) > 0:   
            s = defects[:,0][:,0]
            cx, cy = centroid

            x = np.array(contour[s][:,0][:,0], dtype=np.float)
            y = np.array(contour[s][:,0][:,1], dtype=np.float)

            xp = cv2.pow(cv2.subtract(x, cx), 2)
            yp = cv2.pow(cv2.subtract(y, cy), 2)
            dist = cv2.sqrt(cv2.add(xp, yp))

            dist_max_i = np.argmax(dist)

            if dist_max_i < len(s):
                farthest_defect = s[dist_max_i]
                farthest_point = tuple(contour[farthest_defect][0])
                
                return farthest_point
            
    return None