# coding: utf-8
import pygame, eventlet, time

from objects import HilgaWidget
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
        self.odofile = open(opts['--odo-file'], 'r+')
        self.overall = int(self.odofile.readline())
        # Seek to the end of file
        self.odofile.seek(0, 2)

        self.current = 0
        self.step = 0

        self.odostart_time = 0
        self.gps_speed = 0
        self.gps_ts = time.time()
        gpsiface.add_hook('onupdate', self.on_gpsupdate)

    def odo_increase(self, meters):
        """Increase odometer values."""
        self.overall += meters
        self.current += meters
        self.step + meters

    def update_odofile(self):
        self.odofile.write('{} {}\n'.format(int(time), self.step))
        self.step = 0

        # Update overall
        self.odofile.seek(0, 0)
        self.odofile.write('%20s\n'%self.overall)
        self.odofile.seek(0, 2)

    def on_gpsupdate(self, gps):
        # in meters per sec
        gspeed = 10.0/36 * self.gps.speed_kmh()
        gts = time.time()
        delta = (gspeed - self.gps_speed) * (gts - self.gps_ts)
        self.odo_increase(delta)
        self.gps_speed = gspeed
        self.gps_ts = gts

        # Write updates only when car stops, but less then every 100 meters
        if int(self.gps_speed) == 0 and self.step > 100:
            self.update_odofile()


class OdoWidget(HilgaWidget):
    def __init__(self, odoiface, (x, y), **opts):
        HilgaWidget.__init__(self, (x, y, SW_WIDTH, SW_WIDTH*2))

        self.odo = odoiface
        self.odo_all = -1
        self.odo_cur = -1

        self.fnt = load_font("Anton.ttf", 32)

    def draw(self, tick, surf):
        if self.odo.overall != self.odo_all or \
           self.odo.current != self.odo_cur:
            x, y = self.position
            self.surf.blit(self.fnt.render("ODO: %d", True, (255,255,255)), (x, y))
            self.surf.blit(self.fnt.render("TRP: %d", True, (255,255,255)), (x, y+36))

            # update values
            self.odo_all = self.odo.overall
            self.odo_cur = self.odo.current

        self.redraw_into(surf)
