#!/usr/bin/env python
### Rotary encoder, using interrupts.

from objects import HilgaObject
#from mixer import HilgaMixer
from RPi import GPIO
import eventlet

__all__ = ["HilgaRotary"]

class HilgaRotary(HilgaObject):
    def __init__(self, pin_a, pin_b, pin_sw=None, **opts):
        """Connect A/B to digital pins and common to the GND.
Options
~~~~~~~
  min_pos - minimal rotary position (default=unlimited)
  max_pos - maximal rotary position (default=unlimited)
  position - initial rotary position
  debounce - debounce time (default=10)"""
        HilgaObject.__init__(self, **opts)

#        self.hm = HilgaMixer()

        self.min_pos = opts.get('min_pos', None)
        self.max_pos = opts.get('max_pos', None)
        self.position = opts.get('position', 0)
        self.pqueue = eventlet.Queue()

        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_sw = pin_sw

        # Setup rotary pins
        GPIO.setup(self.pin_a, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self.pin_b, GPIO.IN, GPIO.PUD_UP)
        self._levels = {pin_a: GPIO.input(self.pin_a), pin_b: GPIO.input(self.pin_b)}

        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self.pin_pulse,
                              bouncetime=self.opts.get('debounce', 10))
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self.pin_pulse,
                              bouncetime=self.opts.get('debounce', 10))

        # Setup switch pin
        if self.pin_sw:
            GPIO.setup(self.pin_sw, GPIO.IN)#, GPIO.PUD_UP)
            GPIO.add_event_detect(self.pin_sw, GPIO.BOTH, callback=self.pin_switch, bouncetime=120)

    def pin_switch(self, pin):
        level = GPIO.input(pin)
        self.pqueue.put_nowait((self, 'switch', level))
        print "SW", (self, 'switch', level)

    def pin_pulse(self, pin):
        level = GPIO.input(pin)
        if level == self._levels[pin]:
            # WTF?
            return

        self._levels[pin] = level

        # if A levels signals than it is CW, otherwise CCW
        same_levels = self._levels[self.pin_a] == self._levels[self.pin_b]
        if same_levels:
            self.inc_position(+1 if pin == self.pin_a else -1)

    def inc_position(self, step):
        self.position += step

        if self.min_pos is not None and self.position <= self.min_pos:
            self.position = self.min_pos
        elif self.max_pos is not None and self.position >= self.max_pos:
            self.position = self.max_pos

        self.pqueue.put_nowait((self, 'pos', step, self.position))
        print "POS", (self, 'pos', step, self.position)

#        self.hm.volume_diff(step*100)

    def gen_events(self):
        while not self.isdone:
            ev = self.pqueue.get()
            print "EV", ev
            yield ev #self.pqueue.get()
