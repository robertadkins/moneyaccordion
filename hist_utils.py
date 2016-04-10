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
    print "shape:", frame.shape
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0,1], hist, [0,180,0,256], 1)
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
    cv2.filter2D(dst, -1, disc, dst)

    # cv2.imshow("frame2", dst)

    ret, thresh = cv2.threshold(dst, 100, 255, 0)
    thresh = cv2.merge((thresh,thresh, thresh))

    cv2.GaussianBlur(dst, (3,3), 0, dst)

    return cv2.bitwise_and(frame, thresh)

def get_color_point(frame, hist):
    isolated_frame = hist_filter(frame, hist)
    
    gray = cv2.cvtColor(isolated_frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 100, 255, 0)
    
    M = cv2.moments(thresh)

    dM01 = M['m01']
    dM10 = M['m10']
    dArea = M['m00']
    if (dArea < 10000):
        print "Object not found."
        return None
    else:
        return (dM10 / dArea, dM01 / dArea)

def find_hand_farthest_point(frame, hist, bill_center):
    MAX_DISTANCE_FROM_CENTER = 200
    
    hand_isolated_frame = hist_filter(frame, hist)

    gray = cv2.cvtColor(hand_isolated_frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, 0)
    #_,contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

        moments = cv2.moments(largest_contour)
        centroid = None
        if moments['m00'] != 0:
            cx = int(moments['m10']/moments['m00'])
            cy = int(moments['m01']/moments['m00'])
            centroid = (cx,cy)

        defects = None
        non_returnpoints_hull = cv2.convexHull(largest_contour, returnPoints=False)
        if non_returnpoints_hull is not None and len(non_returnpoints_hull) > 3 and len(largest_contour) > 3:
            defects = cv2.convexityDefects(largest_contour, non_returnpoints_hull)

        if centroid is not None and defects is not None and len(defects) > 0:
            s = defects[:,0][:,0]
            cx, cy = centroid

            x = np.array(largest_contour[s][:,0][:,0], dtype=np.float)
            y = np.array(largest_contour[s][:,0][:,1], dtype=np.float)

            to_delete = []
            for i in range(len(x)):
                if (x[i] - bill_center[0]) * (x[i] - bill_center[0])\
                + (y[i] - bill_center[1]) * (y[i] - bill_center[1])\
                > MAX_DISTANCE_FROM_CENTER * MAX_DISTANCE_FROM_CENTER:
                    to_delete.append(i)
            x = np.delete(x, to_delete)
            y = np.delete(y, to_delete)

            if len(x) > 0:
                xp = cv2.pow(cv2.subtract(x, cx), 2)
                yp = cv2.pow(cv2.subtract(y, cy), 2)
                dist = cv2.sqrt(cv2.add(xp, yp))

                dist_max_i = np.argmax(dist)

                if dist_max_i < len(s):
                    farthest_defect = s[dist_max_i]
                    farthest_point = tuple(largest_contour[farthest_defect][0])
                
                    for cnt in contours:
                        if cnt is not largest_contour:
                            cv2.drawContours(hand_isolated_frame, cnt, -1, (255,0,0), 3)
                        else:
                            cv2.drawContours(hand_isolated_frame, cnt, -1, (0,255,0), 3)

                        cv2.circle(hand_isolated_frame, centroid, 5, [0,255,0], -1)
                        cv2.circle(hand_isolated_frame, farthest_point, 5, [0,0,255], -1)
                        cv2.imshow("hand", hand_isolated_frame)
                        return dist[dist_max_i], farthest_point, hand_isolated_frame
            
    return None, None, None
