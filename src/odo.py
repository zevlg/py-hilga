# coding: utf-8
import pygame, eventlet, time

from objects import HilgaObject, HilgaWidget
from speed import AvgValue
from misc import load_font

CLK_COLOR = (255,255,255)

class OdoIface(HilgaObject):
    """Odometer
Save odometer data to file.
First line in odo file is:

         OVERALL_METERS

so first line is 20 chars length not including \n.
Following lines are entries in form:
TIMESTAMP METERS\n
"""
    def __init__(self, gpsiface, **opts):
        super(OdoIface, self).__init__(**opts)
        self.gps = gpsiface

        self.odofile = open(opts['--odo-file'], 'r+')
        self.overall = float(self.odofile.readline())
        # Seek to the end of file
        self.odofile.seek(0, 2)

        self.current = 0
        self.step = 0

        self.avg_start = None
        self.avg_speed = AvgValue()
        self.gps.add_hook('gotclock', self.set_avg_start)
        self.gps.add_hook('onupdate', self.on_gpsupdate)

    def set_avg_start(self, seconds):
        self.avg_start = seconds

    def odo_increase(self, meters):
        """Increase odometer values."""
        self.overall += meters
        self.current += meters
        self.step += meters

        if meters > 0:
            self.run_hook('onincrease', meters)

    def update_odofile(self):
        self.odofile.write('{} {}\n'.format(int(time.time()), self.step))

        # Prepare to move again
        self.step = 0
        self.avg_speed.reset()
        self.avg_start = time.time()

        # Update overall
        self.odofile.seek(0, 0)
        self.odofile.write('%20s\n'%self.overall)
        self.odofile.seek(0, 2)
        self.run_hook('odoflush')

    def avg_time_delta(self):
        if self.avg_start is None:
            return 0
        return time.time() - self.avg_start

    def on_gpsupdate(self, gps):
        # in meters per sec
        gspeed = 10.0/36 * self.gps.speed_kmh()
        avgspeed = self.avg_speed.avg_with(gspeed)
        delta = avgspeed * self.avg_time_delta() - self.step

        self.odo_increase(delta)

        # Write updates only when car stops, but less then every 100 meters
        if int(gspeed) == 0 and self.step > 100:
            self.update_odofile()


class OdoWidget(HilgaWidget):
    TRP_COLOR = (200, 200, 200)
    ODO_COLOR = (150, 150, 150)
    def __init__(self, odoiface, (x, y), **opts):
        HilgaWidget.__init__(self, (x, y, 32*5, 64))

        self.odo = odoiface
        self.odo_all = -1
        self.odo_cur = -1

        self.need_redraw = True
        self.odo.add_hook('onincrease', self.set_need_redrw)
        self.fnt = load_font("Anton.ttf", 24)

    def set_need_redrw(self, *args):
        self.need_redraw = True

    def draw(self, tick, surf):
        # Sample every third tick
        if tick % 3 != 0:
            return

        if self.need_redraw:
            oall = self.odo.overall / (1000*1000.0)
            cur = self.odo.current / 1000.0
            self.clear()
            self.surf.blit(self.fnt.render("TRP: %.1fKm"%cur, True, self.TRP_COLOR), (0, 0))
            self.surf.blit(self.fnt.render("ODO: %.1fKKm"%oall, True, self.ODO_COLOR), (0, 30))

            # update values
            self.odo_all = self.odo.overall
            self.odo_cur = self.odo.current

        self.redraw_into(surf)
        self.need_redraw = False
