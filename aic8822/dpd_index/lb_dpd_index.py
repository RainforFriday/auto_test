import os
import sys
import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *

global UARTc


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


def MS_EVMPWR_vs_setpwr():
    CSV_NAME = "./data/F2442_ms_evmpwr_vs_setpwr_MCS11_40M_20240626_7c.csv"
    l_results = []

    for pwr_num in range(26):
        UARTc.sendcmd("setpwr " + str(int(pwr_num)))
        reg_index = UARTc.read_reg("403422C8")
        am_pm_bypass_value = UARTc.read_reg_bits("403422c8", "23:22")

        CMPX.wlan_meas_start()
        time.sleep(2)
        peak_pwr = CMPX.wlan_meas_peak_pwr()
        CMPX.wlan_set_peakpwr(int(float(peak_pwr)) + 3)
        CMPX.wlan_meas_abort()

        CMPX.wlan_meas_start()
        time.sleep(2)
        pwr = CMPX.wlan_meas_pwr()
        evm = CMPX.wlan_meas_evm()
        CMPX.wlan_meas_abort()
        result = "{},{},{},{},{}\n".format(pwr_num, reg_index, pwr, evm, am_pm_bypass_value)
        l_results.append(result)
        print(result)

    UARTc.sendcmd("settx 0")

    with open(CSV_NAME, "w") as CSV_DATA:
        CSV_DATA.writelines(l_results)


def MS_EVMPWR_vs_DigIndex():
    CSV_NAME = "./data/F5775_ms_evmpwr_vs_digindex_MCS11_80M_ANAINDEX_F.csv"
    # Low Band
    #TX_GAINMAP_REG_VALUE = "CD3F4766"
    #TX_GAINMAP_REG_VALUE = "CD3F4A71"
    #TX_GAINMAP_REG_VALUE = "D43F4B7A"
    #TX_GAINMAP_REG_VALUE = "D33F4C85"
    #TX_GAINMAP_REG_VALUE = "DA3F4D91"

    # High Band 5775
    #TX_GAINMAP_REG_VALUE = "C33F5579"
    #TX_GAINMAP_REG_VALUE = "C43F5679"
    #TX_GAINMAP_REG_VALUE = "CF3F587E"
    #TX_GAINMAP_REG_VALUE = "D63F597F"
    #TX_GAINMAP_REG_VALUE = "D53F5A7D"
    #TX_GAINMAP_REG_VALUE = "DB3F5C80"
    #TX_GAINMAP_REG_VALUE = "DA3F5D79"
    #TX_GAINMAP_REG_VALUE = "D93F5EE2"
    TX_GAINMAP_REG_VALUE = "D83F5FCF"


    Dig_Start = int("20", 16)
    Dig_Stop = int("F0", 16)
    Dig_Step = 4

    l_results = []

    # tx gain map dr
    UARTc.write_reg_bits("40342274", "31", 1)

    # tx gain map reg
    # UARTc.write_reg("40342270", TX_GAINMAP_REG_VALUE)
    UARTc.sendcmd("w 40342270 {}".format(TX_GAINMAP_REG_VALUE))

    UARTc.sendcmd("settx 1")

    for pwr_num in range(Dig_Start, Dig_Stop, Dig_Step):
        UARTc.write_reg_bits("40342270", "7:0", pwr_num)
        reg_index = UARTc.read_reg("40342270")

        CMPX.wlan_meas_start()
        time.sleep(2)
        peak_pwr = CMPX.wlan_meas_peak_pwr()
        CMPX.wlan_set_peakpwr(int(float(peak_pwr)) + 3)
        CMPX.wlan_meas_abort()

        CMPX.wlan_meas_start()
        time.sleep(2)
        pwr = CMPX.wlan_meas_pwr()
        evm = CMPX.wlan_meas_evm()
        CMPX.wlan_meas_abort()
        result = "{},{},{},{}\n".format(pwr_num, reg_index, pwr, evm)
        l_results.append(result)
        print(result)

    UARTc.sendcmd("settx 0")

    # release tx gain map dr
    UARTc.write_reg_bits("40342274", "31", 0)

    with open(CSV_NAME, "w") as CSV_DATA:
        CSV_DATA.writelines(l_results)


if __name__ == "__main__":
    global UARTc

    UARTc = uart_open(8)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    MS_EVMPWR_vs_setpwr()
    #MS_EVMPWR_vs_DigIndex()
