# Based on http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html

import numpy as np
import cv2
from matplotlib import pyplot as plt

dollar_image = cv2.imread('dollar_sm.jpg', cv2.IMREAD_UNCHANGED)

dollar_image_gray = cv2.cvtColor(dollar_image, cv2.COLOR_BGR2GRAY)
    #dollar_image = cv2.medianBlur(dollar_image, 3)
    
source_image = cv2.imread('dollar2.jpg', cv2.IMREAD_UNCHANGED)
source_image_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

orb = cv2.AKAZE_create()

print "Starting detect and compute"
# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(dollar_image_gray,None)
print "Done 1"
kp2, des2 = orb.detectAndCompute(source_image_gray,None)
print "Done 2"

# create BFMatcher object
bf = cv2.BFMatcher()
#bf = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = bf.knnMatch(des1,des2,k=2)

# Match descriptors.
#matches = bf.match(des1,des2)

# Sort them in the order of their distance.
#matches = sorted(matches, key = lambda x:x.distance)

good = []
for m,n in matches:
    if m.distance < 0.75*n.distance:
        good.append([m])

# Draw first 10 matches.
#img3 = cv2.drawMatches(dollar_image_gray,kp1,source_image_gray,kp2,matches[0:5], None, flags=2)
img3 = cv2.drawMatchesKnn(cv2.cvtColor(dollar_image, cv2.COLOR_BGR2RGB),kp1,cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB),kp2,good, None, flags=2)

plt.imshow(img3),plt.show()