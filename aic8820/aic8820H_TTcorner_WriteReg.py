import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
import os
import sys
from aic8820.csv import *


def test_evm():
    pass


if __name__ == "__main__":

    UARTc = Uart(7)
    UARTc.open()

    # pa_vh_vbit = 0
    # avss_hd1 = 4
    dtmx_vh_vbit =2
    dtmx_vlo_vbit = 7
    dtmx_dac_cscd_vbit = 15
    # UARTc.write_reg_mask("4034402c", "13:11", pa_vh_vbit)
    # UARTc.write_reg_mask("40344038", "3:0", avss_hd1)
    UARTc.write_reg_mask("40344040", "12:10", dtmx_vh_vbit)
    UARTc.write_reg_mask("40344040", "9:7", dtmx_vlo_vbit)
    UARTc.write_reg_mask("40344040", "6:3", dtmx_dac_cscd_vbit)

    UARTc.close()

