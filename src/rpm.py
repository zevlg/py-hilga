import pygame, sys
from math import pi

from obdiface import ObdIface
from gauge import HilgaGauge
from misc import FPS, load_font, play_sound

ASTART = pi/3
ASTOP = pi + pi/6

RPM_MIN = 0
RPM_MAX = 6000.0

class RpmWidget(HilgaGauge):
    def __init__(self, obdiface, (x, y), **opts):
        HilgaGauge.__init__(self, (x, y, 220, 440),
                            ("0", "1", "2", "3", "4", "5", "6"),
                            (RPM_MIN, RPM_MAX),
                            (ASTART, ASTOP),
                            ptype="long", pcolor=(180,0,0), **opts)

        self.obd = obdiface
        self.obd.rpm = self.rpm = 0
        self.load = None

        self.fnt = load_font("Anton.ttf", 32)

    def draw(self, tick, surf):
        # Sample every tick
        rpm = self.obd.rpm = self.obd.sensor(ObdIface.RPM_IDX)
        if tick % FPS*2 == 0:
            load = self.obd.sensor(ObdIface.LOAD_IDX)
        else:
            load = self.load

        # redraw
        if self.rpm != rpm:
            # gauge pointer
            self.redraw_pointer(rpm)

            self.surf.blit(self.fnt.render("%d"%rpm, True, (50,50,50)), (60, 300))
            self.surf.blit(self.fnt.render("%d%%"%int(round(load)), True, (100,100,100)), (140,300))
#            self.surf.blit(self.fnt.render("Load%%: %d"%int(round(load)), True, (110,110,110)), (40, 340))

        self.redraw_into(surf)
        self.rpm = rpm
        self.load = load
