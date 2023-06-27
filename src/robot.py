import atexit
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from settings import settings
from src.display import Display
from src.image import Image
from src.camera import Camera
from src.drivetrain import Drivetrain
from src.autodrive import AutoDrive
from src.collector import ImageCollector
from src.utils import cuda_to_jpeg, detect
from jetson_utils import Log
import numpy as np


class Robot(SingletonConfigurable):

    drivetrain = traitlets.Instance(Drivetrain)
    input = traitlets.Instance(Camera)
    collector = traitlets.Instance(ImageCollector)
    stereo = traitlets.Bool(default_value=True, config=True)
    autodrive = traitlets.Instance(AutoDrive)
    logger = traitlets.Instance(Display)
    image1 = traitlets.Instance(Image)
    image2 = traitlets.Instance(Image,allow_None = True)
    detected = traitlets.Instance(Image)

    def log(self, text):
        self.logger.log(text)


    def __init__(self, *args, **kwargs):

        super(Robot, self).__init__(*args, **kwargs)

        # start logger
        self.logger = Display.instance()

        self.log("starting robot...")

        # start drivetrain
        self.drivetrain = Drivetrain.instance()

        self.autodrive = AutoDrive.instance(config=settings.default_model)

        # start image collector
        self.collector = ImageCollector.instance(config=settings.default_model)

        # start input 1
        self.log("starting camera 1...")
        self.image1 = Image()
        self.image2 = Image()
        self.input = Camera.instance()
        self.input.read()
        self.input.running = True

        traitlets.dlink((self.input, 'value1'), (self.image1, 'value'), transform=cuda_to_jpeg)
        traitlets.dlink((self.input, 'value2'), (self.image2, 'value'), transform=detect)

        self.autodrive.observe(self._on_autodrive_change, 'running')

        self.log("done.")
    
        self.log("...robot started.")


    def get_image(self, index: int):
        if index == 1:
            return self.image1.value if self.image1 else None
        else:
            return self.image2.value if self.image2 else None

        
    def _on_autodrive_change(self, change):
        Log.Verbose(f"Autodrive status changed from {change['old']} to {change['new']}")
        if change['new'] and not change['old']:
            self.drivetrain.stop()
            self.input.observe(self.autodrive.drive, 'value1')
        else:
            
            self.input.unobserve(self.autodrive.drive)
            self.drivetrain.stop()

        

    

   
