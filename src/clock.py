import pygame, eventlet, time

from objects import HilgaWidget
from misc import load_font

CLK_COLOR = (255,255,255)

class ClockWidget(HilgaWidget):
    def __init__(self, obdiface, (x, y), period=5, **opts):
        HilgaWidget.__init__(self, (x, y, 120, 32), **opts)
        self.period = period
        self.time = ""
        self.newtime = time.strftime("%H:%M")

        self.fnt = load_font("Anton.ttf", 18)

        self.pool.spawn_n(self.loop_time)

    def loop_time(self):
        while not self.isdone:
            eventlet.sleep(self.period)
            self.newtime = time.strftime("%H:%M")

    def draw(self, tick, surf):
        if self.newtime != self.time:
            self.clear()
            self.surf.blit(self.fnt.render("TIME: {}".format(self.newtime), True, CLK_COLOR), (0,0))

        self.redraw_into(surf)
        self.time = self.newtime
