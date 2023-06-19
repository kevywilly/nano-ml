import atexit

import traitlets
from Adafruit_MotorHAT import Adafruit_MotorHAT
from traitlets.config.configurable import SingletonConfigurable

from settings import settings
from src.logging.display import Display
from src.motion.motor import Motor
from src.visual.image import Image
from src.visual.camera import Camera
from src.visual.utils import bgr8_to_jpeg, cuda_to_jpeg, merge_3d
from jetson_utils import cudaImage, cudaMemcpy, cudaToNumpy, cudaAllocMapped, cudaConvertColor, cudaDeviceSynchronize
import numpy as np


class Robot(SingletonConfigurable):
    camera = traitlets.Instance(Camera)
    logger = traitlets.Instance(Display)
    image = traitlets.Instance(Image)
    
    m1 = traitlets.Instance(Motor)
    m2 = traitlets.Instance(Motor)
    m3 = traitlets.Instance(Motor, allow_none=True)
    m4 = traitlets.Instance(Motor, allow_none=True)

    i2c_bus = traitlets.Integer(default_value=1).tag(config=True)
    mode = traitlets.Integer(default_value=2).tag(config=True)
    m1_channel = traitlets.Integer(default_value=1).tag(config=True)
    m1_alpha = traitlets.Float(default_value=settings.m1_alpha).tag(config=True)
    m2_channel = traitlets.Integer(default_value=2).tag(config=True)
    m2_alpha = traitlets.Float(default_value=settings.m2_alpha).tag(config=True)
    m3_channel = traitlets.Integer(default_value=3).tag(config=True)
    m3_alpha = traitlets.Float(default_value=settings.m3_alpha).tag(config=True)
    m4_channel = traitlets.Integer(default_value=4).tag(config=True)
    m4_alpha = traitlets.Float(default_value=settings.m4_alpha).tag(config=True)

    def log(self, text):
        self.logger.log(text)

    def __init__(self, *args, **kwargs):

        super(Robot, self).__init__(*args, **kwargs)

        self.logger = Display()
        self.log("Starting robot...")
        self._start_camera()
        self._start_motors()
        self.log("...robot started.")

        

        atexit.register(self.stop)
        
            
    def _callback_fn(self, value):
        #img = cudaMemcpy(value)
        #cudaDeviceSynchronize()
        self.image.value = cuda_to_jpeg(value)
        cudaDeviceSynchronize()
        #del img

    def _start_motors(self):

        self.log("Starting motors...")

        self.motor_driver = Adafruit_MotorHAT(addr=0x60, i2c_bus=self.i2c_bus)

        self.m1 = Motor(self.motor_driver, channel=self.m1_channel, alpha=self.m1_alpha)
        self.m2 = Motor(self.motor_driver, channel=self.m2_channel, alpha=self.m2_alpha)
        self.m3 = Motor(self.motor_driver, channel=self.m3_channel, alpha=self.m3_alpha)
        self.m4 = Motor(self.motor_driver, channel=self.m4_channel, alpha=self.m4_alpha)
        self.motors = [self.m1, self.m2, self.m3, self.m4]

        self.log("...done.")

    def _start_camera(self):

        self.log("Starting camera...")

        self.image = Image()

        self.camera = Camera()
        
        self.camera.read()

        self.camera.running = True

        traitlets.dlink((self.camera, 'value'), (self.image, 'value'), transform=cuda_to_jpeg)
        
        self.log("...done.")

    def shutdown(self):
        self.log("Shutting down robot...")
        self.stop()
        self.camera.release()

    def get_image(self):
        return self.image.value

    def set_motors(self, speeds):
        for idx, speed in enumerate(speeds):
            self.motors[idx].value = speed

    def forward(self, speed=0.3):
        self.log(f"MV: Forward {speed}.")
        for motor in self.motors:
            motor.value = speed

    def backward(self, speed=1.0):
        self.log(f"MV: Backward {speed}.")
        for motor in self.motors:
            motor.value = -speed

    def left(self, speed=1.0):
        self.log(f"MV: Left {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = speed if idx % 2 else -speed

    def slide_left(self, speed=1.0):
        self.log(f"MV: Left {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = -speed if (idx == 0 or idx == 3) else speed

    def forward_left(self, speed=1.0):
        self.log(f"MV: SRight {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = 0 if (idx == 0 or idx == 3) else speed

    def backward_left(self, speed=1.0):
        self.log(f"MV: SRight {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = 0 if (idx == 0 or idx == 3) else -speed

    def right(self, speed=1.0):
        self.log(f"MV: Right {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = -speed if idx % 2 else speed

    def slide_right(self, speed=1.0):
        self.log(f"MV: SRight {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = speed if (idx == 0 or idx == 3) else -speed

    def forward_right(self, speed=1.0):
        self.log(f"MV: SRight {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = speed if (idx == 0 or idx == 3) else 0

    def backward_right(self, speed=1.0):
        self.log(f"MV: SRight {speed}.")
        for idx, motor in enumerate(self.motors):
            motor.value = -speed if (idx == 0 or idx == 3) else 0

    def stop(self):
        self.log(f"MV: Stop.")
        for motor in self.motors:
            motor.value = 0

    def drive(self, cmd: str, speed: float):
        cmd = cmd.lower()
        s = speed

        if cmd == "forward":
            self.forward(s)
        elif cmd == "forward_right":
            self.forward_right(s)
        elif cmd == "forward_left":
            self.forward_left(s)
        elif cmd == "backward":
            self.backward(s)
        elif cmd == "backward_right":
            self.backward_right(s)
        elif cmd == "backward_left":
            self.backward_left(s)
        elif cmd == "left":
            self.left(s)
        elif cmd == "right":
            self.right(s)
        elif cmd == "slide_left":
            self.slide_left(s)
        elif cmd == "slide_right":
            self.slide_right(s)
        else:
            self.stop()
