import traitlets
from traitlets.config.configurable import SingletonConfigurable
from src.visual.utils import bgr8_to_jpeg
from src.visual.stereo_csi_camera import StereoCSICamera
from src.visual.image import Image
import numpy as np
import atexit

class Camera(SingletonConfigurable):

    value0 = traitlets.Any()
    value1 = traitlets.Any()
    vconcat = traitlets.Any()
    image0 = traitlets.Any()
    image1 = traitlets.Any()
    iconcat = traitlets.Any()
    camera = traitlets.Any()

    # config
    width = traitlets.Integer(default_value=224).tag(config=True)
    height = traitlets.Integer(default_value=224).tag(config=True)
    fps = traitlets.Integer(default_value=30).tag(config=True)
    capture_width = traitlets.Integer(default_value=816).tag(config=True)
    capture_height = traitlets.Integer(default_value=616).tag(config=True)

    def __init__(self, *args, **kwargs):
        super(Camera,self).__init__(*args, **kwargs)
        self.value0 = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.value1 = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.vconcat = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.camera_link = None

        atexit.register(self.stop)

    def start(self):
        if self.camera:
            return
        
        print(f"Starting Camera")
      
        self.camera = StereoCSICamera(
            width=self.width, 
            height=self.height, 
            capture_width=self.capture_width, 
            capture_height=self.capture_height, 
            capture_fps=30
            )
        
        
       
        self.image0 = Image()
        self.image1 = Image()
        self.iconcat = Image()
        
        traitlets.dlink((self.camera, 'value0'), (self, 'value0'))
        traitlets.dlink((self.camera, 'value0'), (self.image0, 'value'), transform=bgr8_to_jpeg)
        traitlets.dlink((self.camera, 'value1'), (self, 'value1'))
        traitlets.dlink((self.camera, 'value1'), (self.image1, 'value'), transform=bgr8_to_jpeg)
        traitlets.dlink((self.camera, 'vconcat'), (self, 'vconcat'))
        traitlets.dlink((self.camera, 'vconcat'), (self.iconcat, 'value'), transform=bgr8_to_jpeg)

        self.camera.read()
        
        self.camera.running = True

    def stop(self):
        print("\nReleasing camera...\n")
        self.camera.running = False
        self.camera.release()