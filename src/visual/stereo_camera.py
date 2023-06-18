import threading
import numpy as np
import traitlets
import atexit

from jetson_inference import detectNet as net
from jetson_utils import (
    videoSource,
    cudaDeviceSynchronize
    )
import cv2 as cv
import traitlets
from src.visual.utils import merge_3d
from jetson_utils import cudaMemcpy



class StereoCamera(traitlets.HasTraits):
    left_source = traitlets.Unicode(default_value="csi://0")
    right_source = traitlets.Unicode(default_value="csi://1")
    
    value_right = traitlets.Any()
    value_left = traitlets.Any()

    def __init__(self, callback_fn, *args, **kwargs):
        super(StereoCamera, self).__init__(*args, **kwargs)
        self.height=720
        self.width=1280
        
        self.value_left = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.value_right = np.empty((self.height, self.width, 3), dtype=np.uint8)
  
        self.camera_left = videoSource(self.left_source)
        self.camera_right = videoSource(self.right_source)
        self.callback_fn = callback_fn
        self._running = False


    def _read(self):
        self.value_left = self.camera_left.Capture()
        self.value_right = self.camera_right.Capture()
        self.callback_fn(self.value_left, self.value_right)
        

    def read(self):
        if self._running:
            raise RuntimeError('Cannot read directly while camera is running')
        self._read()
        return self.value_left, self.value_right

    def _capture_frames(self):
        while True:
            if not self._running:
                break
            self._read()

    @traitlets.observe('running')
    def _on_running(self, change):
        if change['new'] and not change['old']:
            # transition from not running -> running
            self._running = True
            self.thread = threading.Thread(target=self._capture_frames)
            self.thread.start()
        elif change['old'] and not change['new']:
            # transition from running -> not running
            self._running = False
            self.thread.join()
