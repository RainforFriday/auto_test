import os
import sys
import numpy
import time
from aicintf.uart import *
from aicintf.com import *
from aicbasic.AIC_C_CODE_LOG import *


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


def msadc_dcinit():
    UARTc.sendcmd("w 40100038 000001A0")
    UARTc.sendcmd("w 4010E008  4003000")
    UARTc.sendcmd("w 4010E00C  C0EA5E7")


def msadc_ms():
    UARTc.sendcmd("w 4010E004 00000001")
    time.sleep(0.028)
    msadc_reg_value = UARTc.read_reg("4010d010")
    volt = (int(msadc_reg_value, 16)/131328.0-1.0)*1214.0
    return volt


if __name__ == "__main__":
    print("aic")