import threading

import traitlets
from jetson_utils import videoSource
from traitlets.config.configurable import SingletonConfigurable

'''
# must disable NVMM
cd jetson-inference/build
cmake -DENABLE_NVMM=off ../
make
sudo make install
'''


class Camera(SingletonConfigurable):
    width = traitlets.Integer(default_value=1280, config=True)
    height = traitlets.Integer(default_value=720, config=True)
    source = traitlets.Unicode(default_value="csi://0", config=True)
    running = traitlets.Bool(default_value=False)
    camera = traitlets.Any()
    value = traitlets.Any()

    def __init__(self, *args, **kwargs):

        super(Camera, self).__init__(*args, **kwargs)
        self.camera = videoSource(self.source, argv=['--input-flip=rotate-180'])
        self._running = False

    def _read(self):
        img = self.camera.Capture()
        if img is not None:
            self.value = img

    def read(self):
        if self._running:
            raise RuntimeError('Cannot read directly while camera is running')
        self._read()
        return self.value

    def _capture_frames(self):
        while True:
            if not self._running:
                break
            self._read()

    @traitlets.observe('running')
    def _on_running(self, change):
        if not self.camera.IsStreaming():
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
