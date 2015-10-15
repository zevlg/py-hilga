# Interface to D100 Huawei router

import pygame
import eventlet, json
from eventlet.green import urllib2

from objects import HilgaObject, HilgaWidget
from misc import load_font, play_sound

__all__ = ["D100Iface", "D100Widget"]

# SCRIPT = '''
# {"ppp_state":<% at_ppp_state_get(); %>,
#  "modem_state":<%modem_state_get();%>,
#  "evdoLevel":<% AT_PPP_get("signal intensity"); %>,
#  "ppp_link_stat":<% AT_PPP_get("ppp link stat"); %>,
#  "operator_rat":<% AT_PPP_get("operator"); %>,
#  "sysinfo":<% sysinfo_get();# '''

SCRIPT = '''
  {"pppState":<% at_ppp_state_get(); %>,
   "evdoLevel":<% AT_PPP_get("signal intensity"); %>,
   "sysinfo":<% sysinfo_get();%>
}
'''

# pppState
PPP_NO_MODEM     = -2
PPP_DISCONNECTED = -1
PPP_CONNECTING   = 0
PPP_CONNECTED    = 1

# evdoLevel  aka signal_intensity
EVDO_LEVEL_ZERO  = 0
EVDO_LEVEL_ONE   = 1
EVDO_LEVEL_TWO   = 2
EVDO_LEVEL_THREE = 3
EVDO_LEVEL_FOUR  = 4
EVDO_LEVEL_FIVE  = 5

# network_type aka sysinfo[6]
NTYPES = {0:"NONE", 1:"GSM", 2:"GPRS", 3:"EDGE", 4:"WCDMA", 5:"HSDPA", 6:"HSUPA", 7:"HSPA"}
NO_SERVICE = 0
GSM        = 1
GPRS       = 2
EDGE       = 3
WCDMA      = 4
HSDPA      = 5
HSUPA      = 6
HSPA       = 7

class D100Iface(HilgaObject):
    def __init__(self, addr='192.168.1.1', period=3, **opts):
        HilgaObject.__init__(self, **opts)

        self.status = {"pppState":-1, "evdoLevel":0, "sysinfo":[-1, -1, -1, -1, -1, -1]}
        self.script_name = "status.asp"
        self.d100_addr = addr
        self.period = period

        self.get_status()

        self.pool.spawn_n(self.loop_d100)

    def get_status(self):
        import time
        try:
            hconn = urllib2.urlopen("http://%s/%s"%(self.d100_addr, self.script_name), None, 5)
            data = hconn.read()
            self.status = json.loads(data)
            hconn.close()
        except:
            return None

        return self.status

    def loop_d100(self):
        while not self.isdone:
            eventlet.sleep(self.period)

            if not self.get_status():
                self.upload_script()
                self.get_status()

    def upload_script(self, login="admin", passwd="admin"):
        import pexpect
        try:
            p = pexpect.spawn('telnet %s'%self.d100_addr)
            p.expect("login:")
            p.sendline(login)
            p.expect("Password:")
            p.sendline(passwd)
            p.expect("#")
            p.sendline("cat > /tmp/3w/%s"%self.script_name)
            p.send(SCRIPT)
            p.sendeof()
            p.sendline("exit")

            p.interact()
            p.close()
        except:
            pass

class D100Widget(HilgaWidget):
    def __init__(self, d100iface, (x, y), **opts):
        HilgaWidget.__init__(self, (x, y, 80, 140), **opts)

        # Instance of D100Iface
        self.d100 = d100iface
        self.prevstatus = {}

        self.fnt = load_font("Anton.ttf", 32)

    def get_contype(self, status):
        si = status.get("sysinfo", [0]*7)
        if type(si) == list and len(si) > 6:
            ntype = si[6]
        else:
            ntype = 0 
        return ntype

    def draw(self, tick, surf):
        newstatus = self.d100.status
        if newstatus != self.prevstatus:
            # Needs redraw
            self.clear()

            # Draw signal bar
            boff = 0
            yoff = 60
            for i in range(EVDO_LEVEL_FIVE+1):
                col = (0, 200, 0) if i <= newstatus.get("evdoLevel", 0) else (50, 50, 50)
                pygame.draw.rect(self.surf, col, pygame.Rect(boff, yoff-i*10, 8, 10+i*10), 0)
                boff += 10

            # ppstate - color for network_type
            pstate = newstatus.get("pppState", -1)
            ntype = self.get_contype(newstatus)
#            print "NTYPE", ntype, "SYSINFO", newstatus.get("sysinfo", None)

            if pstate == PPP_CONNECTED:
                nv = 36*ntype
                if nv > 255:
                    nv = 255
                pcol = (0, nv, 0)
            elif pstate == PPP_CONNECTING:
                pcol = (200, 200, 0)
            else:
                pcol = (200, 0, 0)

            ntlabel = NTYPES.get(ntype, "UNK"+str(ntype))
            self.surf.blit(self.fnt.render(ntlabel, True, pcol), (0, 64))

            # Play sound
            if pstate == PPP_CONNECTED:
                ptype = self.get_contype(self.prevstatus)
                if ptype < HSUPA and ntype >= HSUPA and ntype <= HSPA:
                    play_sound("laugh1.wav")
                elif ptype < EDGE and ntype >= EDGE and ntype <= HSPA:
                    play_sound("jump1.wav")

        self.redraw_into(surf)
        self.prevstatus = newstatus
