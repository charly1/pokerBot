# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 00:54:46 2019

@author: Charly
"""

import cv2
import numpy as np

img_rgb = cv2.imread('test.png')
template = cv2.imread('small.png')
w, h = template.shape[:-1]

res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
threshold = .8
loc = np.where(res >= threshold)
for pt in zip(*loc[::-1]):  # Switch collumns and rows
    cv2.rectangle(img_rgb, pt, (pt[0] + h, pt[1] + w), (0, 0, 255), 2)

#cv2.imwrite('result.png', img_rgb)
cv2.imshow('output',img_rgb)
cv2.waitKey(0)