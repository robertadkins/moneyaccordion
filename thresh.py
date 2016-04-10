import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cv2.namedWindow('thresh', cv2.WINDOW_NORMAL)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

while True:
	ret, frame = cap.read() #read a frame
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	greenLower = (40, 10, 0)
	greenUpper = (120, 255, 255)
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	mask = cv2.bitwise_and(gray, mask)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	if len(cnts) > 0:
		maxcnt = None
		maxarea = 0
		for cnt in cnts:
			newarea = cv2.contourArea(cnt)
			if newarea > maxarea:
				maxarea = newarea
				maxcnt = cnt
		#epsilon = 0.1*cv2.arcLength(maxcnt,True)
		#approx = cv2.approxPolyDP(maxcnt,epsilon,True)
		hull = cv2.convexHull(maxcnt)
		cv2.drawContours(frame,[hull],0,(0,0,255),2)
	
	cv2.imshow('frame', frame)
	cv2.imshow('thresh', mask)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break