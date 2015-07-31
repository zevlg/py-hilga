import pygame
from RPi import GPIO

from objects import HilgaObject, HilgaWidget
from misc import load_font

class PinIface(HilgaObject):
    def __init__(self, pin, **opts):
        HilgaObject.__init__(self, **opts)

        self.pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)
        self.level = GPIO.input(pin)
        self.toggled = True

#        print "LEVEL for", pin, "is", self.level
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.pin_toggle,
                              bouncetime=self.opts.get('debounce', 10))

    def pin_toggle(self, pin):
        self.toggled = True

    def get_level(self):
        if self.toggled:
            self.level = GPIO.input(self.pin)
            self.toggled = False
        return self.level

class PinWidget(HilgaWidget):
    def __init__(self, (x, y, w, h), pin, label, **opts):
        HilgaWidget.__init__(self, (x, y, w, h), **opts)

        self.pinface = PinIface(pin)
        self.label = label

        self.last_level = None
        self.fnt = load_font("Anton.ttf", 24)

    def draw(self, tick, surf):
        level = self.pinface.get_level()
        if self.last_level != level:
            self.clear()
            if not level:
                col = self.opts.get("low_color", (255,0,0))
            else:
                col = self.opts.get("high_color", (10,10,10))
                
            self.surf.blit(self.fnt.render(self.label, True, col), (0,0))

        self.redraw_into(surf)
        self.last_level = level

class HighBeamWidget(PinWidget):
    def __init__(self, (x, y), **opts):
        PinWidget.__init__(self, (x, y, 50, 40), 25, "BEAM",
                           low_color=(80,80,255), **opts)

class OilWidget(PinWidget):
    def __init__(self, (x, y), **opts):
        PinWidget.__init__(self, (x, y, 40, 40), 24, "OIL", **opts)

class BreakWidget(PinWidget):
    def __init__(self, (x, y), **opts):
        PinWidget.__init__(self, (x, y, 40, 40), 23, "BRK", **opts)
