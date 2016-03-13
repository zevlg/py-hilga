import eventlet
eventlet.monkey_patch(socket=True)  # for gps

import gps

from objects import HilgaObject

class GpsIface(HilgaObject):
    """
Hooks:

    `gotclock' - First time clock is received from satellite
                 single arg - utc time in seconds
    `onupdate' - When TPV has been updated
                 single arg - GpsIface
"""
    def __init__(self, **opts):
        super(GpsIface, self).__init__(**opts)
        self.gps = gps.gps(mode=gps.WATCH_ENABLE)

        # True if clock has been set and hook `gotclock' called
        self.gotclock = False

        # Point - time,speed,lng,lat,speed
        self.points = []        # sorted by time

        self.tpv = {}

#        from eventlet import tpool
        self.pool.spawn_n(self.loop_gps)

    def loop_gps(self):
        while not self.isdone:
            data = self.gps.next()

            if not self.gotclock and self.time() is not gps.NaN:
                # Got clock value for the first time
                self.run_hook('gotclock', self.time())
                self.gotclock = True

#            print "DATA class", data.get("class"), len(self.gps.satellites), self.gps.satellites_used
            if data.get("class") == "TPV":
                self.tpv.update(data)
                self.run_hook('onupdate', self)

    def speed_kmh(self):
        return 1.852 * self.speed_knots()

    def speed_knots(self):
        return self.get("speed", 0)

    def get(self, name, default):
        return self.tpv.get(name, default)

    def satellites(self):
        return self.gps.satellites

    def time(self):
        return self.gps.fix.time
