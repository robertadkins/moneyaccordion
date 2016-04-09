import numpy as np
import cv2

squares = []

dollar_image = cv2.imread('dollar.jpg', cv2.IMREAD_UNCHANGED)

# Convert to grayscale
dollar_image_gray = cv2.cvtColor(dollar_image, cv2.COLOR_BGR2GRAY)

thresh = cv2.adaptiveThreshold(dollar_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


def angle(a, b, c):
    return ((a - c).dot(np.transpose(a - c)) + (b - c).dot(np.transpose(b - c)) - (a - b).dot(np.transpose(a - b))) / (2 * (a - c).dot(np.transpose(b - c)))

if not contours:
    print "No contours!"
else:
    # test each contour
    print len(contours)
    for contour in contours:
        # approximate contour with accuracy proportional
        # to the contour perimeter
        result = cv2.approxPolyDP(contour, cv2.arcLength(contour, True)*0.02, True)
        # square contours should have 4 vertices after approximation
        # relatively large area (to filter out noisy contours)
        # and be convex.
        # Note: absolute value of an area is used because
        # area may be positive or negative - in accordance with the
        # contour orientation
        if(len(result) >= 4 or (len(result) == 4 and 
            abs(cv2.contourArea(result)) > 1000 and 
            cv2.isContourConvex(result) )):
           # print "four sided"
            s = 0;
            """for i in range(4):
                # find minimum angle between joint
                # edges (maximum of cosine)
                t = abs(angle( result[i], result[i-2], result[i-1]))
                if s<t:
                    s=t"""
            # if cosines of all angles are small
            # (all angles are ~90 degree) then write quandrange
            # vertices to resultant sequence
            if( s < 0.3 ):
                for i in range(4):
                    squares.append( result )

    #print squares
    
for square in squares:
   # print square
    cv2.rectangle(dollar_image, tuple(square[0][0]), tuple(square[2][0]), (255, 0, 0))
    
cv2.imwrite("thresh.jpg", thresh)
cv2.imwrite("Hi.jpg", dollar_image)