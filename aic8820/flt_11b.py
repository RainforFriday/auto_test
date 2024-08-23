import os
import sys
from aicintf.uart import *


def flt_11b(f0):
    # reg add : 40330320
    # int_txpercoef0  [29:20]
    # int_txpercoef1  [19:10]
    # int_txpercoef2  [9:0]
    #f0 = 400   # 0x190
    #f1 = 130    # 0x082
    #f2 = 0

    # f0 = 400
    f1 = 530 - f0
    f2 = 0

    value = f2*pow(2, 20) + f1*pow(2, 10) + f0
    print(hex(value))

    # AIC8820 FLT ADDR: 40330320
    return value


if __name__ == "__main__":
    #UARTX = Uart(7)
    #UARTX.open()
    value = flt_11b(300)
    print(value)
    # UARTX.write_reg("40330320", value)

