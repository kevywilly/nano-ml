import atexit

import cv2
import traitlets

from src.visual.image_mapper import ImageMapper
from src.visual.stereo_camera import StereoCamera


class StereoCSICamera(StereoCamera):
    capture_device0 = traitlets.Integer(default_value=0)
    capture_device1 = traitlets.Integer(default_value=1)
    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=1280)
    capture_height = traitlets.Integer(default_value=720)
    flip_method = traitlets.Integer(default_value=2)

    def __init__(self, *args, **kwargs):
        super(StereoCSICamera, self).__init__(*args, **kwargs)
        self.mapper = ImageMapper()
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

        atexit.register(self.release)

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
            mvalue_left, mvalue_right = self.mapper.remap(value_left, value_right)
            value_3d = self.mapper.merge_3d(mvalue_left, mvalue_right)
            return value_left, value_right, mvalue_left, mvalue_right, value_3d
        else:
            raise RuntimeError('Could not read image from cameras')
