import subprocess
from enum import Enum

"""
echo 200 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio200/direction
echo 1 > /sys/class/gpio/gpio200/value
echo 38 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio38/direction
echo 1 > /sys/class/gpio/gpio38/value
"""

class GPIODirection(str, Enum):
    OUT: str = "out"
    IN: str = "in"

class GPIOValue(Enum):
    LOW = 0
    HIGH = 1

class GPIO:
    OUT = GPIODirection.OUT
    IN = GPIODirection.IN
    LOW = GPIOValue.LOW
    HIGH = GPIOValue.HIGH

    @staticmethod
    def disable(pin: int):
        try:
            subprocess.call(f"echo {pin} > /sys/class/gpio/unexport")
        except Exception as ex:
            print(ex)

    @staticmethod
    def enable(pin: int):
        try:
            GPIO.disable(pin)
            subprocess.call(f"echo {pin} > /sys/class/gpio/export")
        except Exception as ex:
            print(ex)

    @staticmethod
    def output(pin: int, value: int):
        try:
            subprocess.run(f"echo {value} > /sys/class/gpio/gpio{pin}/value")
        except Exception as ex:
            print(ex)
        
    @staticmethod
    def direction(pin: int, direction: GPIODirection):
        try:
            subprocess.run(f"echo out > /sys/class/gpio/gpio{200}/direction")
        except Exception as ex:
            print(ex)
            
    @staticmethod
    def setup(pin: int, direction: GPIODirection, initial: GPIOValue):
        GPIO.enable(pin)
        GPIO.direction(pin, direction)
        GPIO.output(pin, initial)


