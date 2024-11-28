### AIC8822 APC SET

import os
import sys
from aicbasic.regvalue import *
from aicbasic.regpos import *
from icbasic.aicintf.uart import *

global UARTc


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


def setapc0(endpos, startpos, value, page):
    # start apc
    UARTc.sendcmd("w 403441d0 e")
    UARTc.sendcmd("w 403441b8 222")
    UARTc.sendcmd("w 403441b8 0")
    UARTc.sendcmd("w 403441d0 9")
    UARTc.sendcmd("w 403441b8 444")
    UARTc.sendcmd("w 403441b8 555")

    # edit apc value
    reg_add1 = aicNum(int(aicNum("0x40347090").DEC) + int(page*256)).HEX
    reg_add2 = aicNum(int(aicNum("0x40347094").DEC) + int(page*256)).HEX
    reg_add3 = aicNum(int(aicNum("0x40347098").DEC) + int(page*256)).HEX
    if endpos < 32:
        UARTc.write_reg_mask(reg_add1, "{}:{}".format(endpos, startpos), value)
        print("{} {}:{} {}".format(reg_add1, endpos, startpos, value))
    elif (endpos > 31) and (startpos < 32):
        UARTc.write_reg_mask(reg_add1, "{}:{}".format(31, startpos), value%(value >> (32 - startpos)))
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos-32, 0), value >> (32 - startpos))
    elif (startpos > 31) and (endpos < 64):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos - 32, startpos - 32), value)
    elif (startpos < 64) and (endpos > 63):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(31, startpos-32), value%(value >> (64-startpos)))
        UARTc.write_reg_mask(reg_add3, "{}:{}".format(startpos-64, 0), value >> (64 - startpos))
    elif startpos > 63:
        UARTc.write_reg_mask(reg_add3, endpos-64, startpos-64, value)

    # end apc
    UARTc.sendcmd("w 403441b8 111")
    UARTc.sendcmd("w 403441b8 0")
    UARTc.sendcmd("w 403441b8 222")
    UARTc.sendcmd("w 403441b8 333")
    UARTc.sendcmd("w 403441d0 e")
    UARTc.sendcmd("w 403441d0 6")
    UARTc.sendcmd("w 403441b8 1333")


def apc0_sel(page, index):
    UARTc.write_reg_mask("403441a4", "5:0", "9")
    UARTc.write_reg_mask("403441a4", "6", "1")
    UARTc.write_reg_mask("403441a4", "7", "1")


if __name__ == "__main__":
    UARTc = uart_open(7)
    apc0_sel(0, 0)
    # [apc_end, apc_start, defvalue, regadd, ragpos]
    wf_dac0_vl_it_bit = [4, 0, 15, "40344124", "7:3"]
    wf_dac0_vl_ib_bit = [9, 5, 19, "40344128", "21:17"]
    wf_lb0_tmx_cbit = [16, 13, 7, "40344084", "6:3"]
    wf_lb0_padrv_gbit = [25, 22, 1, "40344088", "15:12"]
    wf_lb0_padrv_cbit = [29, 26, 3, "40344088", "11:8"]
    wf_lb0_padrv_input_cbit = [32, 30, 7, "40344088", "7:5"]
    wf_lb0_pa_input_cbit = [48, 46, 7, "40344098", "22:20"]
    wf_lb0_pa_gbit = [52, 49, 13, "40344098", "19:16"]
    for value in range(3):
        setapc0(4, 0, value, 0)
        print(value)
        valuex = UARTc.read_reg_bits("40344124", "7:3")
        print(valuex)
