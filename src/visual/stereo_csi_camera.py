import atexit

import cv2
import traitlets
from src.visual.utils import crop, merge_3d
from src.visual.stereo_camera import StereoCamera
from settings import calibration_settings as cal
import numpy as np
import cv2 as cv


class StereoCSICamera(StereoCamera):
    capture_device0 = traitlets.Integer(default_value=0)
    capture_device1 = traitlets.Integer(default_value=1)
    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=1280)
    capture_height = traitlets.Integer(default_value=720)
    flip_method = traitlets.Integer(default_value=2)

    value_right = traitlets.Any()
    value_left = traitlets.Any()
    value_3d = traitlets.Any()
    mvalue_left = traitlets.Any()
    mvalue_right = traitlets.Any()

    def __init__(self, *args, **kwargs):
        super(StereoCSICamera, self).__init__(*args, **kwargs)
        if self.format == 'bgr8':
            self.value_left = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.value_right = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.value_3d = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.mvalue_left = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.mvalue_right = np.empty((self.height, self.width, 3), dtype=np.uint8)

        try:
            self.cap_left = cv2.VideoCapture(self._gst_str(self.capture_device0), cv2.CAP_GSTREAMER)
            self.cap_right = cv2.VideoCapture(self._gst_str(self.capture_device1), cv2.CAP_GSTREAMER)

            re0, _ = self.cap_left.read()
            re1, _ = self.cap_right.read()

            if not re0:
                raise RuntimeError('Could not read image from left camera.')

            if not re1:
                raise RuntimeError('Could not read image from right camera.')

        except Exception as ex:
            print(ex)
            raise RuntimeError(
                'Could not initialize camera.  Please see error trace.')

        try:
            cv_file = cv.FileStorage(cal.d3_map_file, cv.FILE_STORAGE_READ)

            self.left_map_1 = cv_file.getNode("left_map_1").mat()
            self.left_map_2 = cv_file.getNode("left_map_2").mat()
            self.right_map_1 = cv_file.getNode("right_map_1").mat()
            self.right_map_2 = cv_file.getNode("right_map_2").mat()

            cv_file.release()
            self.has_map = True
        except:
            pass

        atexit.register(self.release)

    def _remap(self, img1, img2, pct=0.90):
        if self.has_map:
            img1 = crop(cv.remap(img1, self.left_map_1, self.left_map_2, cv.INTER_LINEAR), pct)
            img2 = crop(cv.remap(img2, self.right_map_1, self.right_map_2, cv.INTER_LINEAR), pct)

        return img1, img2

    def release(self):
        print("Releasing Camera...")
        self.running = False
        self.cap_left.release()
        self.cap_right.release()

    def _gst_str(self, device):

        return (
                "nvarguscamerasrc sensor-id=%d ! "
                "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                % (
                    device,
                    self.capture_width,
                    self.capture_height,
                    self.capture_fps,
                    self.flip_method,
                    self.width,
                    self.height
                )
        )

        # return 'nvarguscamerasrc sensor-id=%d ! nvvidconv flip-method=2 ! video/x-raw(memory:NVMM), width=%d, height=%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (
        #        device, self.capture_width, self.capture_height, self.capture_fps, self.width, self.height)

    def _read(self):
        re0, value_left = self.cap_left.read()
        re1, value_right = self.cap_right.read()
        if re0 and re1:
            self.value_left = value_left
            self.value_right = value_right
            self.mvalue_left, self.mvalue_right = self._remap(value_left, value_right)
            self.value_3d = merge_3d(self.mvalue_left, self.mvalue_right)
        else:
            raise RuntimeError('Could not read image from cameras')
