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


def cal_cbit_offset_check():
    UARTc = uart_open(7)

    CHIP_NO = "A0"

    csv_path = "./AIC8820_WF_CBIT_CHECK_20241230_cal.csv"
    csvx = CSV(csv_path)

    csvx.write_append_line("CH, Rate, R403422c8, dtmx_tuning_cbit, pa_input1_cbit, pa_input2_cbit")

    wf_dtmx_tuning_cbit = ["dtmx_tuning_cbit", 80, 77, 3, "40344044", "18:15"]
    wf_pa_input1_cbit = ["pa_input1_cbit", 30, 29, 0, "40344030", "24:23"]
    wf_pa_input2_cbit = ["pa_input2_cbit", 32, 31, 0, "40344030", "22:21"]

    reg_list = [wf_dtmx_tuning_cbit, wf_pa_input1_cbit, wf_pa_input2_cbit]

    setrate = "5 11"

    """
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

    """
    for ch in ["42", "58", "106", "122", "138", "155"]:
        UARTc.sendcmd("setch "+ch)
        time.sleep(5)
        for rate in ["2 7", "2 0"]:
            UARTc.sendcmd("setrate "+str(rate))
            for pwr in range(0, 25):
                UARTc.sendcmd("setpwr "+ str(pwr))
                regvalue = UARTc.read_reg("403422c8")
                value = []
                dtmx_cbit_value = UARTc.read_reg_bits(reg_list[0][4], reg_list[0][5])
                input1_cbit_value = UARTc.read_reg_bits(reg_list[1][4], reg_list[1][5])
                input2_cbit_value = UARTc.read_reg_bits(reg_list[2][4], reg_list[2][5])

                resx = "{},{},{},{},{},{},{}".format(ch, str(pwr), rate, regvalue, dtmx_cbit_value, input1_cbit_value, input2_cbit_value)
                print(resx)
                csvx.write_append_line(resx)


if __name__ == "__main__":
    cal_cbit_offset_check()