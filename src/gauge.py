import pygame
import pygame.gfxdraw
import math

from objects import HilgaWidget
from misc import load_font

GAUGE_WIDTH = 4
ARC_COLOR = (100,100,100)
STROKE_COLOR = (100,100,100)
LABEL_COLOR = (220,220,220)

class HilgaGauge(HilgaWidget):
    """Opts:
  ptype  - type of the pointer: `long' or `short' (default='short')
  pwidth - width of the pointer (default=3)
  pcolor - color of the pointer (default=(255,0,0))
  slength - stroke's (per label) length (default=10)
  loffset - label's offset (default=24)
  fontsize - label's font size (default=16)
"""
    def __init__(self, (x, y, w, h), labels,
                 (min_value, max_value), (start_angle, stop_angle), **opts):
        """Labels - gauge labels.
(min_value, max_value) - Range of the gauge values."""
        HilgaWidget.__init__(self, (x, y, w, h), **opts)

        self.angles = (start_angle, stop_angle)
        self.vlimits = (min_value, max_value)

        # Check for anticlockwise
        self.opposite = min_value > max_value

        # Draw it for the first time
        self.bg = pygame.Surface((w, h))
        fnt = load_font("Anton.ttf", opts.get("fontsize", 16))

        pygame.draw.arc(self.bg, ARC_COLOR, (0, 0, w, h), start_angle, stop_angle, GAUGE_WIDTH)

        vastep = (stop_angle - start_angle)/(len(labels)-1.0)
        vang = start_angle
        slength = opts.get("slength", 10) # stroke's length
        loffset = opts.get("loffset", 24) # label offset
        for lbl in reversed(labels):
            sx, sy = self.get_rpos(vang)
            ex, ey = self.get_rpos(vang, slength)
            pygame.draw.line(self.bg, STROKE_COLOR, (sx, sy), (ex, ey), GAUGE_WIDTH)

            # label
            lbsurf = fnt.render(lbl, True, LABEL_COLOR)
            lbr = lbsurf.get_rect()
            lbr.centerx = self.get_rx(vang, loffset)
            lbr.centery = self.get_ry(vang, 2*loffset)
#            self.bg.blit(fnt.render(lbl, True, LABEL_COLOR), self.get_rpos(vang, 16))
            self.bg.blit(lbsurf, lbr)
            vang += vastep

    def get_rx(self, angle, off=0):
        w, h = self.size
        return w/2 + math.cos(angle)*(w/2-off)
    def get_ry(self, angle, off=0):
        w, h = self.size
        return h/2 - math.sin(angle)*(h/2-off)
    def get_rpos(self, angle, off=0):
        return self.get_rx(angle, off), self.get_ry(angle, 2*off)

    def redraw_pointer(self, value):
        self.surf.blit(self.bg, (0,0))

        pwidth = self.opts.get("pwidth", 3)
        ptype  = self.opts.get("ptype", "short")
        pcolor = self.opts.get("pcolor", (255,0,0))
        w, h = self.size

        # TODO: take into account min_value as well (now 0 is assumed)
        arange = self.angles[1] - self.angles[0]
        vrange = self.vlimits[1] - self.vlimits[0]
        angle = self.angles[0] + ((self.vlimits[1]-value)/vrange)*arange

        px, py = self.get_rpos(angle)
        if ptype == "long":
            pi2 = math.pi/2
            px1 = self.get_rx(angle+pi2, w/2-pwidth)
            py1 = self.get_ry(angle+pi2, h/2-pwidth*2)
            px2 = self.get_rx(angle-pi2, w/2-pwidth)
            py2 = self.get_ry(angle-pi2, h/2-pwidth*2)
        else:
            pi64 = math.pi/64
            px1,py1 = self.get_rpos(angle+pi64, 10)
            px2,py2 = self.get_rpos(angle-pi64, 10)

        pygame.draw.polygon(self.surf, pcolor, [[px, py], [px1, py1], [px2,py2]], 0)
