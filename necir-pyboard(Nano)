# NEC Infrared capture module for MicroPython board
#
# Connect TL1838 receiver to Y10
# (That's a 38kHz IR receiver, as shipped on eBay)
#
# See http://www.sbprojects.com/knowledge/ir/nec.php
#
# Created by MattMatic  2015-04-27 Initial draft
# the version can be got from https://github.com/MattMatic/micropython-necir
# Matt Page / mattmatic@hotmail.com

# Modified by ZhaoTang  2018-03-13 
# changes: MattMatic's version works well on the pyboard platform. 
# But there are some bugs when used on PYB-Nano, which was built by http://www.micropython.org.cn/bbs/forum.php.
# This version used the Pin.irq() attach the rising edge instead of the Timer.channel in MattMatic's version.
# The icw range was determined by experiment and differnt from that in MattMatic's version.
# The usage is the same as the MattMatic's version.

# Usage:
#    def nec_cb(nec, a, c, r)
#        print(a, c, r)				# Address, Command, Repeat
#
#    from necir import NecIr
#    nec = NecIr()
#    nec.callback(nec_cb)

from machine import Pin
import utime
import pyb


class NecIr:
    def __init__(self, pin=pyb.Pin.board.Y10):
        self._ic_start = 0
        self._ic_last = utime.ticks_us()
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
        self._ic_start = utime.ticks_us()
        icw = utime.ticks_diff(self._ic_start, self._ic_last)
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
