# Copyright (C) 2015 by Zajcev Evgeny <zevlg@yandex.ru>

import logging
import pygame

__all__ = ["HilgaObject", "HilgaWidget", "FPS"]

class HilgaObject(object):
    def __init__(self, **opts):
        self.isdone = False
        self.log = logging.getLogger(self.__class__.__name__)

        self.opts = opts
        self.pool = opts.get('pool', None)

    def verbose(self, s, *args):
        self.log.info(s%tuple(args))

class HilgaWidget(HilgaObject):
    def __init__(self, (x, y, w, h), **opts):
        HilgaObject.__init__(self, **opts)

        self.surf = pygame.Surface((w, h))

        self.size = (w, h)
        self.position = (x, y)

    def clear(self):
        self.surf.fill((0,0,0))

    def redraw_into(self, surf):
        surf.blit(self.surf, self.position)
