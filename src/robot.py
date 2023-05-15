import time
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from Adafruit_MotorHAT import Adafruit_MotorHAT
from src.motor import Motor
from src.display import Display
from src.camera import Camera
import atexit
from settings import settings

class Robot(SingletonConfigurable):
    
    camera = traitlets.Instance(Camera)
    left_motor = traitlets.Instance(Motor)
    right_motor = traitlets.Instance(Motor)
    logger = traitlets.Instance(Display)
    
    i2c_bus = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_channel = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_alpha = traitlets.Float(default_value=settings.left_motor_alpha).tag(config=True)
    right_motor_channel = traitlets.Integer(default_value=2).tag(config=True)
    right_motor_alpha = traitlets.Float(default_value=settings.right_motor_alpha).tag(config=True)

    def log(self, text):
        print(text)
        self.logger.log(text)
        
    def __init__(self, *args, **kwargs):
        
        super(Robot, self).__init__(*args, **kwargs)
        self.logger = Display()
        self.log("...")
        self.motor_driver = Adafruit_MotorHAT(addr=0x60, i2c_bus=self.i2c_bus)
        self.left_motor = Motor(self.motor_driver, channel=self.left_motor_channel, alpha=self.left_motor_alpha)
        self.right_motor = Motor(self.motor_driver, channel=self.right_motor_channel, alpha=self.right_motor_alpha)
        self.log("Motors started...")
        self.camera = Camera()
        self.camera.start()
        self.log("Camera started ...")
        
    
    def get_image_capture(self):
        return self.camera.image.value
    
    def set_motors(self, left_speed, right_speed):
        self.left_motor.value = left_speed
        self.right_motor.value = right_speed
        
    def forward(self, speed=0.3, duration=None):
        self.log(f"MV: Forward {speed}.")
        self.left_motor.value = speed
        self.right_motor.value = speed

    def backward(self, speed=1.0):
        self.log(f"MV: Backward {speed}.")
        self.left_motor.value = -speed
        self.right_motor.value = -speed

    def left(self, speed=1.0):
        self.log(f"MV: Left {speed}.")
        self.left_motor.value = -speed
        self.right_motor.value = speed

    def right(self, speed=1.0):
        self.log(f"MV: Right {speed}.")
        self.left_motor.value = speed
        self.right_motor.value = -speed

    def stop(self):
        self.log(f"MV: Stop.")
        self.left_motor.value = 0
        self.right_motor.value = 0

    def drive(self, cmd: str, speed: int):
        c = cmd.lower()
        s = float(max(min(speed,100),0))/100.0

        if cmd == "forward":
            self.forward(s)
        elif cmd == "backward":
            self.backward(s)
        elif cmd == "left":
            self.left(s)
        elif cmd == "right":
            self.right(s)
        else:
            self.stop()
