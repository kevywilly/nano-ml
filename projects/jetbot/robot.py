import time
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from Adafruit_MotorHAT import Adafruit_MotorHAT
from jetbot.motor import Motor
from jetbot.display import Display
from jetbot.camera import Camera

class Robot(SingletonConfigurable):
    
    camera = traitlets.Instance(Camera)
    left_motor = traitlets.Instance(Motor)
    right_motor = traitlets.Instance(Motor)
    logger = traitlets.Instance(Display)
    
    i2c_bus = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_channel = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)
    right_motor_channel = traitlets.Integer(default_value=2).tag(config=True)
    right_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)

    def _log(self, text):
        self.logger.log(text)
        
    def __init__(self, *args, **kwargs):
        
        super(Robot, self).__init__(*args, **kwargs)
        self.logger = Display()
        self._log("...")
        self.motor_driver = Adafruit_MotorHAT(addr=0x60, i2c_bus=self.i2c_bus)
        self.left_motor = Motor(self.motor_driver, channel=self.left_motor_channel, alpha=self.left_motor_alpha)
        self.right_motor = Motor(self.motor_driver, channel=self.right_motor_channel, alpha=self.right_motor_alpha)
        self._log("Motors started...")
        self.camera = Camera()
        self.camera.start()
        self._log("Camera started ...")
        
    
    def get_image_capture(self):
        return self.camera.image.value
    
    def set_motors(self, left_speed, right_speed):
        self.left_motor.value = left_speed
        self.right_motor.value = right_speed
        
    def forward(self, speed=0.3, duration=None):
        self._log(f"MV: Forward {speed}.")
        self.left_motor.value = speed
        self.right_motor.value = speed

    def backward(self, speed=1.0):
        self._log(f"MV: Backward {speed}.")
        self.left_motor.value = -speed
        self.right_motor.value = -speed

    def left(self, speed=1.0):
        self._log(f"MV: Left {speed}.")
        self.left_motor.value = -speed
        self.right_motor.value = speed

    def right(self, speed=1.0):
        self._log(f"MV: Right {speed}.")
        self.left_motor.value = speed
        self.right_motor.value = -speed

    def stop(self):
        self._log(f"MV: Stop.")
        self.left_motor.value = 0
        self.right_motor.value = 0
