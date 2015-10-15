import pygame, eventlet
from math import pi

from obdiface import ObdIface
from gauge import HilgaGauge
from misc import FPS, load_font

ASTART = -pi
ASTOP = -pi/2

COOL_MIN = -40.0
COOL_MAX = 200.0

class CoolantWidget(HilgaGauge):
    def __init__(self, obdiface, (x, y), period=3, **opts):
        HilgaGauge.__init__(self, (x, y, 100, 200),
                            ("C", "", "H"),
                            (COOL_MIN, COOL_MAX),
                            (ASTART, ASTOP),
                            ptype="short", pcolor=(180,0,0), slength=12, loffset=16, fontsize=12,
                            **opts)

        self.period = period
        self.cooltemp = 0

        self.obd = obdiface
        self.obd.cooltemp = self.obd.sensor(ObdIface.COOLTEMP_IDX)

        self.fnt = load_font("Anton.ttf", 18)

        self.pool.spawn_n(self.loop_temp)

    def loop_temp(self):
        while not self.isdone:
            eventlet.sleep(self.period)
            self.obd.cooltemp = self.obd.sensor(ObdIface.COOLTEMP_IDX)

    def draw(self, tick, surf):
        ntemp = self.obd.cooltemp
        if self.cooltemp != ntemp:
            # gauge pointer
            self.redraw_pointer(ntemp)

            self.surf.blit(self.fnt.render(u"%d\u00B0"%ntemp, True, (160,160,160)), (30,90))

            self.redraw_into(surf)

        self.cooltemp = ntemp
