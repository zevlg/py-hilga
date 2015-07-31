# Very simple interface to alsa mixer to control volume

from objects import HilgaObject
from ctypes import *

ASND = CDLL("libasound.so.2")
#ASND.snd_mixer_find_selem.restype = c_void_p;
#ASND.snd_mixer_open.restype = c_int
#ASND.snd_mixer_attach.restype = c_int

class HilgaMixer(HilgaObject):
    def __init__(self, control='PCM', **opts):
        HilgaObject.__init__(self, **opts)

        self.mixer_hndl = c_void_p()
        self.mixer_sid = c_void_p()

        ASND.snd_mixer_open(byref(self.mixer_hndl), 0)
        ASND.snd_mixer_attach(self.mixer_hndl, "hw:0")
        ASND.snd_mixer_selem_register(self.mixer_hndl, 0, 0)
        ASND.snd_mixer_load(self.mixer_hndl)

        ASND.snd_mixer_selem_id_malloc(byref(self.mixer_sid))
        ASND.snd_mixer_selem_id_set_index(self.mixer_sid, 0)
        ASND.snd_mixer_selem_id_set_name(self.mixer_sid, control)
        self.mixer_elem = ASND.snd_mixer_find_selem(self.mixer_hndl, self.mixer_sid)

        pmin = c_long(0)
        pmax = c_long(0)
        ASND.snd_mixer_selem_get_playback_dB_range(self.mixer_elem, byref(pmin), byref(pmax))
        self.db_min = pmin.value
        self.db_max = pmax.value

    def volume_diff(self, db_step):
        cdb = c_long(0)
        ASND.snd_mixer_selem_get_playback_dB(self.mixer_elem, 0, byref(cdb))
        ASND.snd_mixer_selem_set_playback_dB(self.mixer_elem, 0, cdb.value+db_step, 0)

        print "DB", cdb.value + db_step
