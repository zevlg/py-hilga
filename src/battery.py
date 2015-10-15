import pygame, eventlet, re

from obdiface import ObdIface
from objects import HilgaWidget
from misc import load_font, play_sound

BAT_COLOR = (255,255,255)

class BatteryWidget(HilgaWidget):
    def __init__(self, obdiface, (x, y), period=5, **opts):
        HilgaWidget.__init__(self, (x, y, 120, 32), **opts)
        self.period = period
        self.voltage = ""

        self.fnt = load_font("Anton.ttf", 18)

        self.vre = re.compile("([01234567890.]+)V")
        self.obd = obdiface
        self.obd.voltage = self.obd.command("atrv")

        self.pool.spawn_n(self.loop_temp)

    def loop_temp(self):
        while not self.isdone:
            eventlet.sleep(self.period)
            self.obd.voltage = self.obd.command("atrv")

    def check_voltage(self, voltstr, alerton=11.5):
        """Alert if VOLTSTR falls lower than ALERTON."""
        vm = self.vre.match(voltstr)
        if vm:
            vval = float(vm.groups()[0])
            if vval < alerton:
                print "LOW BATTERY! " + voltstr
                play_sound("alert1.wav")

    def draw(self, tick, surf):
        nvolt = self.obd.voltage
        if self.voltage != nvolt:
            self.clear()
            self.surf.blit(self.fnt.render("BAT: {}".format(nvolt), True, BAT_COLOR), (0,0))
            self.check_voltage(nvolt)

        self.redraw_into(surf)
        self.voltage = nvolt
