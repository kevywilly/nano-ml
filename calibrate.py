#!/usr/bin/python3

from settings import settings
from src.visual.calibrator import Calibrator
from src.visual.camera_model import CameraModel
from src.visual.image_mapper import ImageMapper

calibrator = Calibrator()

camera_model: CameraModel = settings.camera_model
if camera_model is None:
    camera_model = calibrator.calibrate()

calibrator.rectify3d(camera_model)


