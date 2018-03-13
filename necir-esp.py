# NEC Infrared capture module for MicroPython ESP32 or ESP8266 board
#
# Connect HX1838B receiver to 35
# (That's a 38kHz IR receiver, as shipped on taobao)
#
#
# Created by Zhao Tang  2018-03-13 Initial draft 
#    Matt Page / tju.tangzhao@gmail.com

# Difference with the version for pyboard(Nano):
# time module (utime module on pyboard)
# pin=35(pyboard can only use the form like: pin=pyb.Pin.board.Y10 and number is not supported)

# Usage:
#    def nec_cb(nec, a, c, r)
#        print(a, c, r)				# Address, Command, Repeat
#
#    from necir import NecIr
#    nec = NecIr()
#    nec.callback(nec_cb)

from machine import Pin
import time


class NecIr:
    def __init__(self, pin=35):
        self._ic_start = 0
        self._ic_last = time.ticks_us()
        self._ic_width = 0
        self._sr = [0, 0, 0, 0]
        self._rst()
        self._address = 0
        self._command = 0
        self._cb = None
        self._ic_pin = Pin(pin, Pin.IN)
        self._ic_pin.irq(trigger=Pin.IRQ_RISING, handler=self._ic_cb)
        self._id = 0

    def _rst(self):
        self._sr[0] = 0
        self._sr[1] = 0
        self._sr[2] = 0
        self._sr[3] = 0
        self._sc = 0
        self._sb = 0

    def _bit(self, v):
        self._sr[self._sb] = (self._sr[self._sb] >> 1) + v
        self._sc = self._sc + 1
        if (self._sc > 7):
            self._sc = 0
            self._sb = self._sb + 1
            if (self._sb > 3):
                if ((self._sr[0] ^ self._sr[1] ^ self._sr[2] ^ self._sr[3]) == 0):
                    self._address = self._sr[0]
                    self._command = self._sr[2]
                    if (self._cb):
                        self._cb(self, self._address, self._command, False)  # Contains the address & command
                self._rst()

    def _ic_cb(self, pin):
        self._ic_start = time.ticks_us()
        icw = time.ticks_diff(self._ic_start, self._ic_last)
        self._ic_last = self._ic_start
        self._ic_width = icw
        self._id += 1
        if (icw > 5500):
            # print('[gap]')  # gap in transmission
            pass
        elif (icw > 4000):
            # print('IR start')
            self._rst()
        elif (icw > 2500):  # Repeat command
            # print('IR repeat')
            if (self._cb):
                self._cb(self, self._address, self._command, True)
        elif (icw > 1500):
            self._bit(0x80)  # High bit
            # print('High bit')
        else:
            self._bit(0x00)  # Low bit
            # print('Low bit')
        # print(self._id, self._ic_width)

    def callback(self, fn):
        self._cb = fn
