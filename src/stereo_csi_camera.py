from src.stereo_camera import StereoCamera
import atexit
import cv2
import numpy as np
import threading
import traitlets


class StereoCSICamera(StereoCamera):
    
    capture_device0 = traitlets.Integer(default_value=0)
    capture_device1 = traitlets.Integer(default_value=1)
    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=640)
    capture_height = traitlets.Integer(default_value=480)
    
    def __init__(self, *args, **kwargs):
        super(StereoCSICamera, self).__init__(*args, **kwargs)
        try:
            self.cap0 = cv2.VideoCapture(self._gst_str(self.capture_device0), cv2.CAP_GSTREAMER)
            self.cap1 = cv2.VideoCapture(self._gst_str(self.capture_device1), cv2.CAP_GSTREAMER)
            
            re0, image = self.cap0.read()
            re1, image = self.cap1.read()

            if not re0:
                raise RuntimeError('Could not read image from camera 0.')

            if not re1:
                raise RuntimeError('Could not read image from camera 1.')
            
        except:
            raise RuntimeError(
                'Could not initialize camera.  Please see error trace.')

        atexit.register(self.release)

    def release(self):
        self.cap0.release()
        self.cap1.release()

    def _gst_str(self, device):
        return 'nvarguscamerasrc sensor-id=%d ! nvvidconv flip-method=2 ! video/x-raw(memory:NVMM), width=%d, height=%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (
                device, self.capture_width, self.capture_height, self.capture_fps, self.width, self.height)
    
    def _read(self):
        re0, image0 = self.cap0.read()
        re1, image1 = self.cap1.read()
        if re0 and re1:
            iconcat = cv2.hconcat([image0, image1])
            return (image0, image1, iconcat)
        else:
            raise RuntimeError('Could not read image from cameras')