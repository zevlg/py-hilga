import pygame, eventlet

from misc import FPS
from objects import HilgaObject
from obdiface import ObdIface
from fuel import FuelIface, FuelWidget, KanistraWidget
from speed import SpeedWidget
from rpm import RpmWidget
from coolant import CoolantWidget
from leds import HighBeamWidget, OilWidget, BreakWidget
from d100 import D100Iface, D100Widget

class HilgaBoard(HilgaObject):
    def __init__(self, **opts):
        HilgaObject.__init__(self, **opts)
        
        self.screen = pygame.display.get_surface()
#        self.board = pygame.Surface((1280, 480))
        self.clock = pygame.time.Clock()
        self.ticks = 0

        fiface = FuelIface(**opts)
        self.fuel = FuelWidget(fiface, (660, 360), **opts)
        self.can = KanistraWidget(fiface, (580, 260), **opts)

        self.obd = obd = ObdIface(**opts) #port="/dev/pts/3", **opts)
        self.speed = SpeedWidget(obd, (274, 20))

        self.rpm = RpmWidget(obd, (10, 120), **opts)
        self.coolant = CoolantWidget(obd, (580, 360), **opts)

        # high beam / oil presure / brake
        self.hbeam = HighBeamWidget((94, 376), **opts)
        self.oil = OilWidget((654, 500), **opts)
        self.brk = BreakWidget((654, 540), **opts)

        d100iface = D100Iface(**opts)
        self.d100 = D100Widget(d100iface, (600, 100))

        self.pool.spawn_n(self.loop_ticks)

    def gen_ticks(self):
        ticks = 0
        while 1:
            yield ticks
            ticks += 1
            eventlet.sleep(1.0/FPS)

    def tick(self):
        # Reconnect obd if disconnected
        if not self.obd.is_connected():
            self.obd.connect()

        # Render widgets
        self.speed.draw(self.ticks, self.screen)
        self.rpm.draw(self.ticks, self.screen)
        self.coolant.draw(self.ticks, self.screen)
        self.fuel.draw(self.ticks, self.screen)
        self.can.draw(self.ticks, self.screen)

        self.hbeam.draw(self.ticks, self.screen)
        self.oil.draw(self.ticks, self.screen)
        self.brk.draw(self.ticks, self.screen)

        self.d100.draw(self.ticks, self.screen)

        self.ticks += 1
        pygame.display.update()

        self.clock.tick(FPS)

    def loop_ticks(self):
        import time
        done = False
        stime = time.time()
        while not done:
#        for tick in self.gen_ticks():
            for pyev in pygame.event.get():
                if pyev.type == pygame.QUIT or \
                       (pyev.type == pygame.KEYUP and pyev.key == pygame.K_ESCAPE):
                    done = True

#             if done:
#                 break

            self.tick()
            eventlet.sleep(0)
#            eventlet.sleep(1./FPS)

#             if self.ticks % 100 == 0:
#                 print "FPS", self.ticks/(time.time()-stime)
