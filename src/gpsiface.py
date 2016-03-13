import eventlet
eventlet.monkey_patch(socket=True)  # for gps

import gps

from objects import HilgaObject

MPS_TO_KPH = 3.6000000000000001
MPS_TO_MPH = 2.2369363
MPS_TO_KNOTS = 1.9438445

class GpsIface(HilgaObject):
    def __init__(self, **opts):
        super(GpsIface, self).__init__(**opts)
        self.gps = gps.gps(mode=gps.WATCH_ENABLE)

        # Point - time,speed,lng,lat,speed
        self.points = []        # sorted by time

        self.tpv = {}

#        from eventlet import tpool
        self.pool.spawn_n(self.loop_gps)

    def loop_gps(self):
        while not self.isdone:
            data = self.gps.next()
#            print "DATA class", data.get("class"), len(self.gps.satellites), self.gps.satellites_used
            if data.get("class") == "TPV":
                self.tpv.update(data)

    def speed_kmh(self):
        return MPS_TO_KPH * self.speed_mps()

    def speed_mps(self):
        return self.get("speed", 0)

    def alt_meters(self):
        return int(round(self.get("alt", -1)))

    def get(self, name, default):
        return self.tpv.get(name, default)

    def satellites(self):
        return self.gps.satellites
