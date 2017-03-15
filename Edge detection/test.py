#coding=utf-8

import cv2
import numpy as np
from matplotlib import pyplot as plt
img = cv2.imread('../image/test2.jpg',cv2.IMREAD_COLOR)
im = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
imgray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,127,155,0)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(im,contours,-1,(0,0,255),3)

print contours[0:51]
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow("image",im)
cv2.waitKey(0)

"""
cv2.imshow("pic",img)
cv2.imwrite(../image/IMG_0358_meitu_1_after.jpg,img)
"""
