import traitlets
from traitlets.config import SingletonConfigurable
from settings import settings
from enum import Enum
from src.gpio import GPIO



class Lights(SingletonConfigurable):

    led_pins = traitlets.List(default_value=settings.led_pins).tag(config=True)
    is_on = traitlets.Bool(default_value=False).tag(config=True)

    def __init__(self, *args, **kwargs):
        super(Lights,self).__init__(*args, **kwargs)
        for pin in self.led_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH if self.is_on else GPIO.LOW)
    
    def set_value(self, value):
        for pin in self.led_pins:
            GPIO.output(pin, value)

    def on(self):
        self.is_on = True
        self.set_value(1)
    
    def off(self):
        self.is_on = False
        self.set_value(0)


