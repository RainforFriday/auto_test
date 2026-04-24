# encoding: utf-8

import os
import sys

from aicinstr.rs.genericinstrument import *

__version__ = "v0.1"


class SGE(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()

    def set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.write("SOURce1:FREQuency:CW {}MHZ".format(cfreq))
        return True

    def set_power(self, pwr):  # pwr unit dbm
        self.write("SOURce1:POWer:POWer {}".format(pwr))
        return True

    def pwr_on(self):
        self.write("OUTPut:ALL:STATe ON")
        return True

    def pwr_off(self):
        self.write("OUTPut:ALL:STATe OFF")
        return True


if __name__ == "__main__":
    host = "10.21.10.182"
    port = 5025
    SGE1 = SGE()
    SGE1.open_tcp(host, port)
    print(SGE1.id_string())
    SGE1.set_cfreq("5000")
    SGE1.set_power("-19")
    SGE1.pwr_on()
