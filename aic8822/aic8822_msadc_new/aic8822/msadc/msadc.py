import os
import sys
import time
import numpy
from icbasic.aicintf.uart import *
from icbasic.aicintf.com import *
from icbasic.aicbasic.AIC_C_CODE_LOG import *



def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc

def uart_close():
    UARTc.close()

def bt_pa_on(UARTc):
    UARTc.sendcmd("w 4058001C 0")
    UARTc.sendcmd("w 40622000 C")

def msadc_rfdc_init(UARTc):
    UARTc.sendcmd("w 40100038 000001A0") 
    UARTc.sendcmd("w 4010E008  4003000") 
    UARTc.sendcmd("w 4010E00C  C0EA5E7")

def msadc_ms(UARTc):
    UARTc.sendcmd("w 4010E004 00000001")
    time.sleep(0.05)
    reg_hexval = UARTc.read_reg("4010E010")
    decval = int(reg_hexval, 16)
    vout = (decval/131328.0-1.0)*1214.0
    return round(vout, 2)


if __name__ == "__main__":

    bt_pa_on()
    msadc_rfdc_init()
    msadc_ms()