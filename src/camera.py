import threading
import traitlets
from jetson_utils import videoSource, cudaMemcpy
from traitlets.config.configurable import SingletonConfigurable
from settings import settings
import atexit

class Camera(SingletonConfigurable):

    stereo = traitlets.Bool(default_value=settings.cam_stereo, config=True)
    width = traitlets.Integer(default_value=1280, config=True)
    height = traitlets.Integer(default_value=720, config=True)
    source1 = traitlets.Unicode(default_value="csi://0", config=True)
    source2 = traitlets.Unicode(default_value="csi://1", config=True)
    running = traitlets.Bool(default_value=False)
    input1 = traitlets.Any()
    input2 = traitlets.Any(allow_none=True)
    value1 = traitlets.Any()
    value2 = traitlets.Any(allow_none=True)
    flip1 = traitlets.Any(allow_none=True)
    flip2 = traitlets.Any(allow_none=True)

    def __init__(self, *args, **kwargs):

        super(Camera, self).__init__(*args, **kwargs)
        self.input1 = videoSource(self.source1, argv=['--input-flip=rotate-180'])
        self.input2 = videoSource(self.source2, argv=['--input-flip=rotate-180'])

        self._running = False
        atexit.register(self._close)


    def _read(self):
        img1 = self.input1.Capture()
        if img1 is not None:
            self.value1 = img1
        else:
            print("invalid capture for input 1")
            return

        
        img2 = self.input2.Capture()
        if img2 is not None:
            self.value2 = img2
        else:
            print("invalid capture for input 2")



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

    def _close(self):
        print("shutting down cameras.")
        self.running = False
        if self.input1:
            self.input1.Close()
        if self.input2:
            self.input2.Close()
