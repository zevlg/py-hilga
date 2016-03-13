import pygame, eventlet, time

from objects import HilgaWidget
from misc import load_font

CLK_COLOR = (255,255,255)

class ClockWidget(HilgaWidget):
    def __init__(self, obdiface, (x, y), period=5, timefun=time.time, **opts):
        HilgaWidget.__init__(self, (x, y, 120, 32), **opts)
        self.timefun = timefun
        self.period = period
        self.time = ""
        self.new_time = self.format_time()

        self.fnt = load_font("Anton.ttf", 18)

        self.pool.spawn_n(self.loop_time)

    def format_time(self, seconds=None):
        return time.strftime("%H:%M", time.localtime(seconds or self.timefun()))

    def loop_time(self):
        while not self.isdone:
            eventlet.sleep(self.period)
            self.new_time = self.format_time()

    def draw(self, tick, surf):
        if self.newtime != self.time:
            self.clear()
            self.surf.blit(self.fnt.render("TIME: {}".format(self.newtime), True, CLK_COLOR), (0,0))

        self.redraw_into(surf)
        self.time = self.newtime

    def set_system_time(self, seconds):
        """Set system clock to seconds"""
        import os
        os.system('date -s "@{}"'.format(seconds))
