import sys
import os
from icbasic.aicintf.uart import *


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


if __name__ == "__main__":
    global UARTc

    UARTc = uart_open(7)
    UARTc.open()

    # lb0 iv_ib_mode, def value: 4
    UARTc.write_reg_mask("403440a4", "16:14", iv_ib_mode)

    # lb0 v_tc_mode, def value: 0
    UARTc.write_reg_mask("403440a4", "28:26", v_tc_mode)

    # lb0 iv_it_mode, def value: 3
    UARTc.write_reg_mask("403440a0", "2:0", iv_it_mode)

    # lb0 vm
    UARTc.write_reg_mask("4034409c", "7:4", vm_cgm_ibit)  # def:15
    UARTc.write_reg_mask("4034409C", "3:0", vm_vtr_ibit)  # def:0
    UARTc.write_reg_mask("403440a0", "14:12", vl_i_itbg_bit)  # def:0
    UARTc.write_reg_mask("403440a0", "11:9", vl_i_itcgm_bit)  # def:4
    UARTc.write_reg_mask("403440a4", "31:29", vl_diode_en)  # def: 3
