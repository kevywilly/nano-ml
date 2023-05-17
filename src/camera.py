import traitlets
from traitlets.config.configurable import SingletonConfigurable
from jetcam.utils import bgr8_to_jpeg
from jetcam.csi_camera import CSICamera
import atexit
import numpy as np
from src.image import Image

class Camera(SingletonConfigurable):

    value = traitlets.Any()
    image = traitlets.Any()
    camera = traitlets.Any()

    # config
    width = traitlets.Integer(default_value=224).tag(config=True)
    height = traitlets.Integer(default_value=224).tag(config=True)
    fps = traitlets.Integer(default_value=30).tag(config=True)
    capture_width = traitlets.Integer(default_value=816).tag(config=True)
    capture_height = traitlets.Integer(default_value=616).tag(config=True)

    def __init__(self, *args, **kwargs):
        self.value = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.camera_link = None
        super(Camera, self).__init__(*args, **kwargs)
        atexit.register(self.stop)

    def start(self):
        if self.camera:
            return
        
        print(f"Starting Camera")
      
        self.camera = CSICamera(
            width=self.width, 
            height=self.height, 
            capture_device=0, 
            capture_width=self.capture_width, 
            capture_height=self.capture_height, 
            capture_fps=30
            )
        
        
       
        self.image = Image()
        
        traitlets.dlink((self.camera, 'value'), (self, 'value'))
        traitlets.dlink((self.camera, 'value'), (self.image, 'value'), transform=bgr8_to_jpeg)

        self.camera.read()
        
        self.camera.running = True

    def stop(self):
        print("\nReleasing camera...\n")
        self.camera.running = False
        self.camera.cap.release()