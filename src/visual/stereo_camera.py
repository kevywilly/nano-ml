import threading
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from jetson_utils import videoSource

class StereoCamera(SingletonConfigurable):

    width = traitlets.Integer(default_value=1280, config=True)
    height = traitlets.Integer(default_value=720, config=True)
    left_source = traitlets.Unicode(default_value = "csi://0", config=True)
    right_source = traitlets.Unicode(default_value = "csi://1", config=True)
    running = traitlets.Bool(default_value=False)
    value_left = traitlets.Any()
    value_right = traitlets.Any()

    def __init__(self, callback_fn = None, *args, **kwargs):

        super(StereoCamera, self).__init__(*args, **kwargs)
  
        self.camera_left = videoSource(self.left_source)
        self.camera_right = videoSource(self.right_source)
        self.callback_fn = callback_fn

        self.value_left = self.camera_left.Capture()
        self.value_right = self.camera_right.Capture()
        
        self._running = False


    def _read(self):
        self.value_left = self.camera_left.Capture()
        self.value_right = self.camera_right.Capture()
        if self.callback_fn:
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
