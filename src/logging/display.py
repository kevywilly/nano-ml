import atexit
import time
from threading import Event, Thread

import Adafruit_SSD1306
import traitlets
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from traitlets.config.configurable import SingletonConfigurable

DEFAULT_TEXT = ["Hello Jetson Nano!", "", "", ""]


class Display(SingletonConfigurable):
    # value = traitlets.Dict(default_value=DEFAULT_TEXT)
    value = traitlets.List(default_value=DEFAULT_TEXT, minlen=0, maxlen=4)
    started = traitlets.Bool(default_value=False, allow_none=False)

    def __init__(self, *args, **kwargs):
        super(Display, self).__init__(*args, **kwargs)
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=1, gpio=1)
        self.event = None
        self.thread = None
        self.start()
        atexit.register(self.stop)

    @traitlets.observe('value')
    def _observe_value(self, change):
        print(f"displaying {change['new']}")

    def start(self):
        print("Starting Display")

        if (self.started):
            return

        self.event = Event()
        self.thread = Thread(target=self._run, args=(self.event,))
        self.thread.start()
        self.started = True

    def stop(self):
        if not self.started:
            return

        if (self.event):
            self.event.set()
        if (self.thread and self.thread.is_alive()):
            self.thread.join(1)

        self.thread = None
        self.event = None
        self.started = False

    def log(self, text):
        print(f"log: {text}")
        self.write(text)

    def write(self, text):
        ar = self.value
        ar.pop()
        ar.insert(0, text)
        self.value = ar

    def _run(self, event):

        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))
        padding = -2
        top = -2
        bottom = height - padding
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        font = ImageFont.load_default()
        x = 0

        while True:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            i = 0
            for (idx, text) in enumerate(self.value):
                draw.text((x, top + (idx * 8)), text, font=font, fill=255)
            self.disp.image(image)
            self.disp.display()
            time.sleep(.1)
            if (event.is_set()):
                self.disp.clear()
                self.disp.display()
                print("Stopping Display")
                break
