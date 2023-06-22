import threading
import traitlets
from jetson_utils import videoSource
from traitlets.config.configurable import SingletonConfigurable

class Camera(SingletonConfigurable):
    stereo = traitlets.Bool(default_value=False, config=True)
    width = traitlets.Integer(default_value=1280, config=True)
    height = traitlets.Integer(default_value=720, config=True)
    source1 = traitlets.Unicode(default_value="csi://0", config=True)
    source2 = traitlets.Unicode(default_value="csi://1", config=True)
    running = traitlets.Bool(default_value=False)
    input1 = traitlets.Any()
    input2 = traitlets.Any(allow_none=True)
    value1 = traitlets.Any()
    value2 = traitlets.Any(allow_none=True)

    def __init__(self, *args, **kwargs):

        super(Camera, self).__init__(*args, **kwargs)
        self.input1 = videoSource(self.source1, argv=['--input-flip=rotate-180'])

        if self.stereo:
            self.input2 = videoSource(self.source2, argv=['--input-flip=rotate-180'])

        self._running = False


    def _read(self):
        img = self.input1.Capture()
        if img is not None:
            self.value1 = img
        else:
            print("invalid capture")

        if self.stereo:
            img2 = self.input2.Capture
            if self.img2 is not None:
                self.value2 = img


    def read(self):
        if self._running:
            raise RuntimeError('Cannot read directly while camera is running')
        self._read()
        return self.value1, self.value2


    def _capture_frames(self):
        while True:
            if not self._running:
                break
            self._read()


    @traitlets.observe('running')
    def _on_running(self, change):
        if not self.input1.IsStreaming():
            self.running = False
            self.thread.join()

        if change['new'] and not change['old']:
            # transition from not running -> running
            self._running = True
            self.thread = threading.Thread(target=self._capture_frames)
            self.thread.start()
        elif change['old'] and not change['new']:
            # transition from running -> not running
            self._running = False
            self.thread.join()