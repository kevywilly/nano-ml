import traitlets
import threading
import numpy as np

class StereoCamera(traitlets.HasTraits):

    value_right = traitlets.Any()
    value_left = traitlets.Any()

    width = traitlets.Integer(default_value=224)
    height = traitlets.Integer(default_value=224)
    format = traitlets.Unicode(default_value='bgr8')
    running = traitlets.Bool(default_value=False)
    
    def __init__(self, *args, **kwargs):
        super(StereoCamera, self).__init__(*args, **kwargs)
        if self.format == 'bgr8':
            self.value_right = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.value_left = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self._running = False
            
    def _read(self):
        """Blocking call to read frame from camera"""
        raise NotImplementedError
        
    def read(self):
        if self._running:
            raise RuntimeError('Cannot read directly while camera is running')
        self.value_right, self.value_left = self._read()
        return self.value_right, self.value_left
    
    def _capture_frames(self):
        while True:
            if not self._running:
                break
            self.value_right, self.value_left = self._read()
            
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