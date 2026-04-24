import os
import sys
import time

from aicbasic.regvalue import *
from aicbasic.regpos import *
from icbasic.aicintf.uart import *
from aic8822.csv import *
from icbasic.aicinstr.rs.cmp180 import *
global UARTc


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


def apc_cbit_offset_check():
    UARTc = uart_open(7)

    CHIP_NO = "A4"

    csv_path = "../AIC8822_WF_CBIT_CHECK_20250207_wiccal.csv"
    csvx = CSV(csv_path)

    csvx.write_append_line("CH, Rate, R403422c8, lb0_tmx_cbit, lb0_padrv_cbit, lb1_tmx_cbit, lb1_padrv_cbit, hb0_tmx_cbit, hb0_padrv_cbit, hb1_tmx_cbit, hb1_padrc_cbit")

    wf_lb0_tmx_cbit = ["lb0_tmx_c", 16, 13, 7, "40344084", "6:3"]
    wf_lb0_padrv_cbit = ["lb0_padrv_c", 29, 26, 3, "40344088", "11:8"]

    wf_lb1_tmx_cbit = ["lb0_tmx_c", 16, 13, 7, "403440f8", "21:18"]
    wf_lb1_padrv_cbit = ["lb0_padrv_c", 29, 26, 3, "403440fc", "24:21"]

    wf_hb0_tmx_cbit = ["hb0_tmx_c", 17, 13, 9, "40344050", "11:7"]
    wf_hb0_padrv_cbit = ["hb0_padrv_c", 31, 27, 16, "40344054", "17:13"]

    wf_hb1_tmx_cbit = ["hb1_tmx_c", 17, 13, 9, "403440c4", "25:21"]
    wf_hb1_padrv_cbit = ["hb1_padrv_c", 31, 27, 16, "403440c8", "31:27"]

    reg_list = [wf_lb0_tmx_cbit, wf_lb0_padrv_cbit, wf_lb1_tmx_cbit, wf_lb1_padrv_cbit,
                wf_hb0_tmx_cbit, wf_hb0_padrv_cbit, wf_hb1_tmx_cbit, wf_hb1_padrv_cbit]

    setrate = "5 11"

    '''
    for ch in ["7"]:
        UARTc.sendcmd("setch "+ch)
        time.sleep(2)
        for rate in ["5 11", "5 0", "0 3"]:
            UARTc.sendcmd("setrate " + rate)
            for pwr in range(0, 25):
                UARTc.sendcmd("setpwr "+ str(pwr))
                regvalue = UARTc.read_reg("403422c8")
                value = []
                for regx in reg_list:
                    value.append(str(UARTc.read_reg_bits(regx[4], regx[5])))
                # print(value)
                resx = "{},{},{},{}".format(ch, rate, regvalue, ",".join(value))
                print(resx)
                csvx.write_append_line(resx)
    '''

    for ch in ["42", "58", "106", "122", "138", "155"]:
        UARTc.sendcmd("setch "+ch)
        time.sleep(2)
        UARTc.sendcmd("setrate 5 11")
        for pwr in range(0, 25):
            UARTc.sendcmd("setpwr "+ str(pwr))
            regvalue = UARTc.read_reg("403422c8")
            value = []
            for regx in reg_list:
                value.append(str(UARTc.read_reg_bits(regx[4], regx[5])))

            resx = "{},{},{},{}".format(ch, "5 11", regvalue, ",".join(value))
            print(resx)
            csvx.write_append_line(resx)


if __name__ == "__main__":
    apc_cbit_offset_check()