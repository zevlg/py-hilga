#!/usr/bin/env python

import sys, os, getopt
import eventlet

srcdir = os.path.abspath(os.path.dirname(__file__)+'/src')
sys.path.insert(0, srcdir)

obddir = os.path.abspath(os.path.dirname(__file__)+'/pyobd')
sys.path.insert(0, obddir)

import pygame
from pygame.locals import *

from board import HilgaBoard

def usage():
   print "usage: [-m] %s"%sys.argv[0]
   print "\t-m  \tMute, no sounds ever"
   sys.exit(0)

def main():
   try:
      opts, args = getopt.getopt(sys.argv[1:], "m", ["odo-file=", "mute"])
   except getopt.GetoptError, err:
      print str(err)
      usage()

   opts = dict(opts)

   pygame.mixer.pre_init(44100, -16, 2, 512)
   pygame.init()
   pygame.mixer.set_num_channels(32)

   vflags = HWSURFACE | DOUBLEBUF | FULLSCREEN
   pygame.display.set_mode((800, 600), vflags)
   pygame.mouse.set_visible(0)

   pool = eventlet.GreenPool()

   board = HilgaBoard(pool=pool, **opts)
#   board.run()

   pool.waitall()

#   import cProfile
#   cProfile.run('HilgaBoard().run()')

if __name__ == "__main__":
    main()
