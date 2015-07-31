import eventlet
import obd_io

from objects import HilgaObject

class ObdIface(HilgaObject):
    LOAD_IDX=4                          # engine load (%)
    COOLTEMP_IDX=5                      # coolant temperature (C)
    RPM_IDX=12                          # engine RPM
    SPEED_IDX=13                        # speed
    ENGINETIME_IDX=31                   # seconds

    def __init__(self, port="/dev/ttyUSB0", **opts):
        HilgaObject.__init__(self, **opts)

        self.portname = port

        self.connect()

    def connect(self):
        self.port = obd_io.OBDPort(self.portname, None, 2, 2)
        if self.port.State == 0:
            self.port.close()
            self.port = None

    def is_connected(self):
        return self.port

    def sensor(self, idx):
        try:
            (_, value, _) = self.port.sensor(idx) if self.port else ("", -1, "")
        except:
            self.port = None
            return -1

        return value
