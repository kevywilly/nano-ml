import threading
import numpy as np
import traitlets

class StereoCamera(traitlets.HasTraits):


    width = traitlets.Integer(default_value=960)
    height = traitlets.Integer(default_value=540)
    format = traitlets.Unicode(default_value='bgr8')
    running = traitlets.Bool(default_value=False)

    def __init__(self, *args, **kwargs):
        super(StereoCamera, self).__init__(*args, **kwargs)
        self._running = False

    def _read(self):
        """Blocking call to read frame from camera"""
        raise NotImplementedError

    def read(self):
        if self._running:
            raise RuntimeError('Cannot read directly while camera is running')
        self._read()
        return self.value_left, self.value_right, self.mvalue_left, self.mvalue_right, self.value_3d

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
