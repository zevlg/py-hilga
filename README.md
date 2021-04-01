# py-hilga

Raspberry Pi based combination meter implemented for my Toyota Hilux,
uses OBD2 and few pins.

Interfaces with:

* GPS module to get clock, altitude, speed and to estimate distances
  for odometer
* OBD2 module to get engine load, engine rpm, coolant temperature,
  battery voltage, dtc codes
* pins from Hilux wiring for Fuel Level, Beam light, hand-brake
  status, oil status
* LTE/5G modem status with triggers when signal switches from EDGE/3G
  to LTE/5G

Screenshot of meter in action:

![screen15](https://zevlg.github.io/py-hilga/meter1.jpg)

# TODO

* "TRP Time" widget to show total trip time along the side with trip
  distance widget
* Compas Widget
* Speed limit widget via openstreetmap's speed_limit

* Meter simulation, to feed meter with synthetic data to see how it
  performs

# Alternatives

* https://github.com/joshellissh/pi-dgc
