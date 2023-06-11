#!/usr/bin/python3
from settings import settings
import cv2 as cv
import glob

filesl = glob.glob(f"{settings.calibration_stereo_left_folder}/*.png")
filesr = glob.glob(f"{settings.calibration_stereo_right_folder}/*.png")

img = cv.imread(filesl[0])
print(img.shape)



for file in filesl:
    img = cv.imread(file)
    img = cv.resize(img,(640,360))
    cv.imwrite(file, img)
    print(file)

for file in filesr:
    img = cv.imread(file)
    img = cv.resize(img,(640,360))
    cv.imwrite(file, img)
    print(file)
