# encoding: utf-8
"""
@version: 0-0
@author: yudunyang
@site:
@software: PyCharm
@file: znd.py
@time: 2022/6/10 19:49
"""

import os
import sys


from pyinstr.rs.genericinstrument import *

__version__ = "v0.1"


class ZND(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()
        self.s_params = ["S11", "S12", "S21","S22"]

    def reset(self):
        self.write("*RST; *OPC?")

    def clear(self):
        self.write("*CLS; *OPC?")

    #  S params set
    def set_Sparams(self, route="S11"):
        if route not in self.s_params:
            print("Set s_params Error, Abort!!!")
            sys.exit(0)
        self.write("CALCulate1:PARameter:MEASure \"Trc1\", \"{}\"".format(route))
        return True

    #mark点设置以及频率设置
    def set_mark(self,mark=1,freq=5800):
        self.write("CALCULATE1:MARKER1 ON".format(mark))
        self.write("CALCULATE1:MARK1:X {}GHz".format(freq/1000))
        return True

    def mark_off(self,mark=1):
        self.write("CALCULATE1:MARKER{} OFF".format(mark))
        return True

    def mark_alloff(self):
        self.write("CALCulate1:MARKer1:AOFF")
        return True

    # 截止频率与开始频率设置
    def set_freq(self,start=2000,end=6000):
        self.write("SENS:FREQ:STAR {}GHz".format(start/1000))
        self.write("SENS:FREQ:STOP {}GHz".format(end/1000))
        return True

    def set_format_smith(self):
        self.write("CALCulate1:FORMat SMITh")
        return True

    def set_format_dbmsg(self):
        self.write("CALCulate1:FORMat MLOGarithmic")
        return True

    def set_format_polar(self):
        self.write("CALCulate1:FORMat POLar")
        return True

    def set_format_real(self):
        self.write("CALCulate1:FORMat REAL")
        return True

    def set_format_imag(self):
        self.write("CALCulate1:FORMat IMAGinary")
        return True

    def read_mark(self,mark=1):
        return self.query("CALCulate1:MARKer{}:FUNCtion:RESult?".format(mark))

    def read_mark_polar_real(self,mark=1):
        self.set_format_polar()
        return self.read_mark(mark).split(",")[1]

    def read_mark_polar_imag(self,mark=1):
        self.set_format_polar()
        return self.read_mark(mark).split(",")[2]

    def read_mark_smith_real(self,mark=1):
        self.set_format_smith()
        return self.read_mark(mark).split(",")[1]

    def read_mark_smith_imag(self,mark=1):
        self.set_format_smith()
        return self.read_mark(mark).split(",")[2]

    def read_mark_dbmsg(self,mark=1):
        self.set_format_dbmsg()
        return self.read_mark(mark).split(",")[1]

    def read_mark_real(self,mark=1):
        self.set_format_real()
        return self.read_mark(mark).split(",")[1]

    def read_mark_imag(self,mark=1):
        self.set_format_imag()
        return self.read_mark(mark).split(",")[1]

if __name__ == "__main__":
    host = "10.21.10.169"
    port = 5025
    ZND1 = ZND()
    ZND1.open_tcp(host, port)
    print(ZND1.id_string())
    #ZND1.set_mark(1,5800)
    #ZND1.set_freq(2000,5900)
    #time.sleep(0.5)
    #ZND1.set_Sparams("S11")


   #print(ZND1.read_mark_polar_real())
    #print(ZND1.read_mark_polar_imag())
    #print(ZND1.read_mark_smith_real())
    #print(ZND1.read_mark_smith_imag())
    #print(ZND1.read_mark_dbmsg())
    #print(ZND1.read_mark_real())
    #print(ZND1.read_mark_imag())
    ZND1.close()