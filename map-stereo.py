#!/usr/bin/python3


from settings import settings
from src.visual.image_mapper import ImageMapper
import os
import cv2 as cv

mapper = ImageMapper()

for filename in os.listdir(settings.calibration_stereo_left_folder):
    img_l = cv.imread(os.path.join(settings.calibration_stereo_left_folder,filename))
    img_r = cv.imread(os.path.join(settings.calibration_stereo_right_folder,filename))

    out = mapper.map_3d(img_l, img_r)
    cv.imwrite(os.path.join(settings.calibration_image_output_folder, f"3d_{filename}"),out)