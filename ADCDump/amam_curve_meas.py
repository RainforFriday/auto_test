# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: amam_curve_meas.py
@time: 2021/8/20 17:41
"""

import os
import sys
from pyintf.uart import *
from pyinstr.rs.fsq import *


if __name__ == "__main__":
    UART1 = Uart(7, True)
    UART1.set_baudrate(921600)
    UART1.open()

    FSQ1 = FSQ()
    FSQ1.open_tcp("10.21.10.109")
    FSQ1.set_analyzer_mode()
    FSQ1.set_cfreq_mhz(5800)
    FSQ1.set_span_mhz(5)
    FSQ1.set_reflvl(30)
    FSQ1.set_rb_mhz(0.05)

    TONE_AMP_REG = "40344030"
    for tone_amp in range(1024):
        UART1.reg_write_bits(TONE_AMP_REG, "10:20", tone_amp)