import eventlet
import smbus
from math import pi

from objects import HilgaObject, HilgaWidget
from gauge import HilgaGauge
from misc import FPS, load_font

__all__ = ["FuelIface", "FuelWidget"]

TANK_VOLUME = 80                        # litres
TANK_EMPTY = 128.0                      # 110 Ohm
TANK_FULL = 24.0                        #  4 Ohm

AIN_ADDR=0x48

LABEL_COL = (100,100,100)
LITRES_COL = (200, 200, 200)

class FuelIface(HilgaObject):
    def __init__(self, period=0.5, nsamples=10, **opts):
        HilgaObject.__init__(self, **opts)

        self.period = period

        self.samples = []

        self.analog = 0                 # analog value [<TANK_EMPTY>..<TANK_FULL>]
        self.litres = 0
        self.percents = 0

        self.bus = smbus.SMBus(0)
        self.get_status()

        self.pool.spawn_n(self.loop_status)

    def get_status(self):
        self.bus.write_byte(AIN_ADDR, 0x40)
        self.bus.read_byte(AIN_ADDR)    # dummy read to start conversion

        val = self.bus.read_byte(AIN_ADDR)
        if val > TANK_EMPTY:
            val = TANK_EMPTY
        self.samples.insert(0, val)
        if len(self.samples) > self.opts.get("nsamples", 10):
            self.samples.pop()

        self.analog = sum(self.samples)/len(self.samples)
        self.percents = (TANK_EMPTY - self.analog)/(TANK_EMPTY - TANK_FULL)
        self.litres = int(TANK_VOLUME*self.percents)

    def loop_status(self):
        while not self.isdone:
            eventlet.sleep(self.period)
            self.get_status()

class FuelWidget(HilgaGauge):
    def __init__(self, fueliface, (x, y), **opts):
        HilgaGauge.__init__(self, (x, y, 100, 200),
                            ["F", "", "E"], # full, half, empty
                            (TANK_FULL, TANK_EMPTY),
                            (-pi/2, 0),
                            ptype="short", slength=12, loffset=16, fontsize=12,
                            **opts)

        # Instance of FuelIface
        self.fuel = fueliface
        self.state = None

        self.fnt = load_font("Anton.ttf", 18)

    def draw(self, tick, surf):
        nstate = (self.fuel.percents, self.fuel.litres)
        if nstate != self.state:
            # gauge pointer
            self.redraw_pointer(self.fuel.analog)

            self.surf.blit(self.fnt.render("%d%%"%(100*nstate[0],), True, LABEL_COL), (30,80))
            self.surf.blit(self.fnt.render("%dL"%nstate[1], True, LITRES_COL), (30,112))
            self.surf.blit(self.fnt.render(" %d "%self.fuel.analog, True, LABEL_COL), (30,144))
#            self.surf.blit(self.fnt.render("Fuel:", True, (100,100,100)), (0,0))
#            self.surf.blit(self.fnt.render("%d%% %dL"%nstate, True, (255,255,255)), (0,32))

        self.redraw_into(surf)
        self.state = nstate

# funny
class KanistraWidget(HilgaGauge):
    def __init__(self, fueliface, (x, y), **opts):
        HilgaGauge.__init__(self, (x, y, 100, 200),
                            ["0", "5", "10", "15", "20"], # full, half, empty
                            (0, 20), (-pi/4, pi+pi/4),
                            ptype="long", slength=12, loffset=16, fontsize=16,
                            **opts)

        # Instance of FuelIface
        self.fuel = fueliface
        self.state = None

        self.fnt = load_font("Anton.ttf", 18)

    def draw(self, tick, surf):
        nstate = (self.fuel.percents, self.fuel.litres)
        if nstate != self.state:
            # gauge pointer
            self.redraw_pointer(20)

            self.surf.blit(self.fnt.render("20LITRES", True, LABEL_COL), (30,80))
#            self.surf.blit(self.fnt.render("Fuel:", True, (100,100,100)), (0,0))
#            self.surf.blit(self.fnt.render("%d%% %dL"%nstate, True, (255,255,255)), (0,32))

        self.redraw_into(surf)
        self.state = nstate
