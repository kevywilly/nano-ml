import traitlets
from traitlets.config.configurable import SingletonConfigurable
from jetcam.utils import bgr8_to_jpeg
from jetcam.csi_camera import CSICamera
import atexit
import numpy as np

class Image(traitlets.HasTraits):
    value = traitlets.Any()

class Camera(SingletonConfigurable):

    value = traitlets.Any()
    image = traitlets.Any()
    camera = traitlets.Any()

    # config
    width = traitlets.Integer(default_value=224).tag(config=True)
    height = traitlets.Integer(default_value=224).tag(config=True)
    fps = traitlets.Integer(default_value=30).tag(config=True)
    capture_width = traitlets.Integer(default_value=1080).tag(config=True)
    capture_height = traitlets.Integer(default_value=760).tag(config=True)

    def __init__(self, *args, **kwargs):
        self.value = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.camera_link = None
        super(Camera, self).__init__(*args, **kwargs)
        atexit.register(self.stop)

    def start(self):
        if self.camera:
            return
        print("Starting Camera")
        self.camera = CSICamera(
            width=self.width, 
            height=self.height, 
            capture_device=0, 
            capture_width=self.capture_width, 
            capture_height=self.capture_height, 
            capture_fps=30
            )
        self.camera.running = True
        self.image = Image()
        self._camera_link = traitlets.dlink((self.camera, 'value'), (self.image, 'value'), transform=bgr8_to_jpeg)

    def stop(self):
        print("\nReleasing camera...\n")
        if self._camera_link:
            self._camera_link.unlink()

        self.camera.running = False
        self.camera.cap.release()