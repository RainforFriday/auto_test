import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
import os
import sys
from aic8820.csv import *


def test_evm():
    pass


if __name__ == "__main__":
    csv_name = "./data/aic8820h_tt_evm_resval_20241113_1624.csv"

    UARTc = Uart(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    CSVX = CSV(csv_name)

    vl1_res_reg_addr = "40344030"
    vl1_res_bit_start = "0"
    vl1_res_bit_stop = "2"

    vl2_res_reg_addr = "40344034"
    vl2_res_bit_start = "12"
    vl2_res_bit_stop = "14"

    vl1_vbit_reg_addr = "40344030"
    vl1_vbit_start = "7"
    vl1_vbit_stop = "9"

    vl2_vbit_reg_addr = "40344034"
    vl2_vbit_start = "19"
    vl2_vbit_stop = "21"

    for ch in [42]:
        for resval in range(0, 8, 1):
            # write res value
            UARTc.write_reg_mask(vl1_res_reg_addr, vl1_res_bit_stop + ":" + vl1_res_bit_start, str(resval))
            UARTc.write_reg_mask(vl2_res_reg_addr, vl2_res_bit_stop + ":" + vl2_res_bit_start, str(resval))
            resx1 = UARTc.read_reg_bits(vl1_res_reg_addr, vl1_res_bit_stop + ":" + vl1_res_bit_start)
            resx2 = UARTc.read_reg_bits(vl2_res_reg_addr, vl2_res_bit_stop + ":" + vl2_res_bit_start)
            vbit1 = UARTc.read_reg_bits(vl1_vbit_reg_addr, vl1_vbit_stop + ":" + vl1_vbit_start)
            vbit2 = UARTc.read_reg_bits(vl2_vbit_reg_addr, vl2_vbit_stop + ":" + vl2_vbit_start)

            # print("res1: " + str(resx1))
            # print("res2: " + str(resx2))


            # cal dpd
            ch_freq = str(int(5000) + int(ch*5))
            UARTc.sendcmd("settx 0")
            UARTc.sendcmd("setbw 0 0")
            UARTc.sendcmd("calib 1 80007000 132 2 1 " + ch_freq)
            time.sleep(2)
            UARTc.sendcmd("settx 1")

            # cmp180 setting
            CMPX.wlan_set_standard("11ax")
            CMPX.wlan_set_bandwidth("20")
            CMPX.wlan_set_freq_by_ch(ch)
            CMPX.wlan_auto_peak_pwr()
            CMPX.wlan_meas_start()
            time.sleep(2)

            # measure evm and power
            ms_pwr = CMPX.wlan_meas_pwr()
            ms_evm = CMPX.wlan_meas_evm()
            CMPX.wlan_meas_abort()

            # write results
            results = "{},{},{},{},{},{},{}".format(ch, resx1, resx2, vbit1, vbit2, ms_pwr, ms_evm)
            CSVX.write_append_line(results)
