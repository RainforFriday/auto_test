import serial   # pip install pyserial
import serial.tools.list_ports
import re
import sys
import time
import pyprind
import xmodem
from aicintf.uart import *
from aicintf.com import *
from aicbasic.aiclog import *
def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


if __name__ == "__main__":
    global uart0,csv_name,cva_name1,dvdd_result
    #csv_name = "aic8820h_spec_testability(2).csv"
    comport = 12
    uart0 = uart_open(comport)
    uart0.sendcmd("w 40506008 4338000")
    uart0.sendcmd("w 40580018 3")
    uart0.sendcmd("w 40100038 28")
    uart0.sendcmd("w 40100038 128")
    uart0.sendcmd("w 4010d008 02003000")
    uart0.sendcmd("w 4010d00c 0a0ea5e5")
    for i in range(0,2,1):
        uart0.write_reg_mask("4034400c", "30:15", 0)
        uart0.write_reg_mask("4034400c", "15", 1)
        uart0.write_reg_mask("40344008", "2:0", 0)
        time.sleep(0.001)
        print(uart0.read_reg("4034400c"))
        print(uart0.read_reg("40502018"))
        uart0.sendcmd("w 4010d004 1")
        time.sleep(0.002)
        rdata1=uart0.read_reg_bits("4010d010","21:0")
        print(int(rdata1)*1214/32896-1214)
        time.sleep(0.001)
        uart0.write_reg_mask("4034400c", "30:15", 0)
        uart0.write_reg_mask("4034400c", "24", 1)
        #uart0.write_reg_mask("40502018", "14:11", 1)
        uart0.write_reg_mask("40344008", "2:0", 5)
        #print(uart0.read_reg("4034400c"))
        #print(uart0.read_reg("40502018"))
        time.sleep(0.001)
        uart0.sendcmd("w 4010d004 1")
        time.sleep(0.002)
        rdata2 = uart0.read_reg_bits("4010d010", "21:0")
        print(int(rdata2)*1214/32896-1214)
        time.sleep(0.001)
        print("\n")
        #uart0.write_reg_mask("4034400c", "30:15", 0)
        #uart0.write_reg_mask("40502018", "14:11", 0)
    uart0.close()