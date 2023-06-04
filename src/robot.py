import time
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from Adafruit_MotorHAT import Adafruit_MotorHAT
from src.stereo_csi_camera import StereoCSICamera
from src.motor import Motor
from src.display import Display
import atexit
from settings import settings
from src.image import Image
from jetcam.utils import bgr8_to_jpeg

class Robot(SingletonConfigurable):
    
    camera = traitlets.Instance(StereoCSICamera)
    logger = traitlets.Instance(Display)
    rimage = traitlets.Instance(Image)
    limage = traitlets.Instance(Image)
    image = traitlets.Instance(Image)

    m1 = traitlets.Instance(Motor)
    m2 = traitlets.Instance(Motor)
    m3 = traitlets.Instance(Motor, allow_none=True)
    m4 = traitlets.Instance(Motor, allow_none=True)
    
    i2c_bus = traitlets.Integer(default_value=1).tag(config=True)
    mode = traitlets.Integer(default_value=1).tag(config=True)
    m1_channel = traitlets.Integer(default_value=1).tag(config=True)
    m1_alpha = traitlets.Float(default_value=settings.m1_alpha).tag(config=True)
    m2_channel = traitlets.Integer(default_value=2).tag(config=True)
    m2_alpha = traitlets.Float(default_value=settings.m2_alpha).tag(config=True)
    m3_channel = traitlets.Integer(default_value=3).tag(config=True)
    m3_alpha = traitlets.Float(default_value=settings.m3_alpha).tag(config=True)
    m4_channel = traitlets.Integer(default_value=4).tag(config=True)
    m4_alpha = traitlets.Float(default_value=settings.m4_alpha).tag(config=True)

    cam_width = traitlets.Integer(default_value=224).tag(config=True)
    cam_height = traitlets.Integer(default_value=224).tag(config=True)
    cam_fps = traitlets.Integer(default_value=30).tag(config=True)
    cam_capture_width = traitlets.Integer(default_value=816).tag(config=True)
    cam_capture_height = traitlets.Integer(default_value=616).tag(config=True)

    def log(self, text):
        self.logger.log(text)
        
    def __init__(self, *args, **kwargs):
        
        super(Robot, self).__init__(*args, **kwargs)
        self.logger = Display()
        self.log("...")
        self.motor_driver = Adafruit_MotorHAT(addr=0x60, i2c_bus=self.i2c_bus)
        
        self.m1 = Motor(self.motor_driver, channel=self.m1_channel, alpha=self.m1_alpha)
        self.m2 = Motor(self.motor_driver, channel=self.m2_channel, alpha=self.m2_alpha)
        self.m3 = Motor(self.motor_driver, channel=self.m3_channel, alpha=self.m3_alpha)
        self.m4 = Motor(self.motor_driver, channel=self.m4_channel, alpha=self.m4_alpha)
        self.motors = [self.m1, self.m2, self.m3, self.m4]
        
        self.log("Motors started...")

        self.image = Image()
        self.rimage = Image()
        self.limage = Image()

        self.camera = StereoCSICamera(
            width=self.cam_width, 
            height=self.cam_height, 
            capture_width=self.cam_capture_width, 
            capture_height=self.cam_capture_height, 
            capture_fps=30
            )
        
        # self.camera = Camera.instance()
        # self.camera.start()

        self.camera.read()
        self.camera.running = True

        self.log("Camera started ...")

        traitlets.dlink((self.camera, 'rvalue'), (self.rimage, 'value'), transform=bgr8_to_jpeg)
        traitlets.dlink((self.camera, 'lvalue'), (self.limage, 'value'), transform=bgr8_to_jpeg)
        traitlets.dlink((self.camera, 'cvalue'), (self.image, 'value'), transform=bgr8_to_jpeg)

        atexit.register(self.stop)
    
    def shutdown(self):
        self.log("Shutting down robot...")
        self.stop()
        self.camera.release()
        # self.camera.release()

    def get_image_capture(self):
        return self.image.value
    
    def get_images(self):
        return {"left" : self.limage.value, "right" : self.rimage.value, "concat": self.image.value}
    
    def set_motors(self, speeds):
        for idx, speed in enumerate(speeds):
            self.motors[idx].value = speed

    def forward(self, speed=0.3, duration=None):
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
        elif cmd == "foward_left":
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

