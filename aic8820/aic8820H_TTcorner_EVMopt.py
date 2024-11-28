import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
import os
import sys
from aic8820.csv import *


def test_evm():
    pass


if __name__ == "__main__":
    csv_name = "./data/aic8820h_tt_evm_resval_20241119_1026.csv"

    UARTc = Uart(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    CSVX = CSV(csv_name)
    csv_header = "ch, pa_vh_vbit, avss_hd1, dtmx_vh_vbit, dtmx_vlo_vbit, dtmx_dac_cscd_vbit, ms_pwr, ms_evm"
    CSVX.write_append_line("Transferring testmode_8820h_test.bin...")
    CSVX.write_append_line(csv_header)

    UARTc.sendcmd("settx 1")

    """
    for ch in ["42", "58", "106", "122", "138", "155"]:
        UARTc.sendcmd("setch "+str(ch))
        time.sleep(2)
        CMPX.wlan_set_freq_by_ch(str(ch))
        for pa_vh_vbit in range(0, 8, 1):
            UARTc.write_reg_mask("4034402c", "13:11", str(pa_vh_vbit))
            for avss_hd1 in range(0, 16, 1):
                UARTc.write_reg_mask("40344038", "3:0", str(avss_hd1))
                for dtmx_vh_vbit in range(0, 8, 1):
                    UARTc.write_reg_mask("40344040", "12:10", str(dtmx_vh_vbit))
                    for dtmx_vlo_vbit in range(0, 8, 1):
                        UARTc.write_reg_mask("40344040", "9:7", str(dtmx_vlo_vbit))
                        for dtmx_dac_cscd_vbit in range(0, 16, 1):
                            UARTc.write_reg_mask("40344040", "6:3", str(dtmx_dac_cscd_vbit))
                            UARTc.sendcmd("setch "+str(ch))
                            time.sleep(2)

                            # set cmp180
                            CMPX.wlan_auto_peak_pwr()
                            CMPX.wlan_meas_start()
                            time.sleep(2)

                            # measure evm and power
                            ms_pwr = CMPX.wlan_meas_pwr()
                            ms_evm = CMPX.wlan_meas_evm()
                            CMPX.wlan_meas_abort()

                            # write results
                            results = "{},{},{},{},{},{},{},{}".format(ch, pa_vh_vbit, avss_hd1, dtmx_vh_vbit, dtmx_vlo_vbit, dtmx_dac_cscd_vbit, ms_pwr, ms_evm)
                            CSVX.write_append_line(results)

                            print(results)
    """
    for ch in ["42", "58", "106", "122", "138", "155"]:
        UARTc.sendcmd("setch "+str(ch))
        time.sleep(2)
        CMPX.wlan_set_freq_by_ch(str(ch))
        pa_vh_vbit = 0
        avss_hd1 = 4
        dtmx_vh_vbit =2
        dtmx_vlo_vbit = 7
        dtmx_dac_cscd_vbit = 15
        UARTc.write_reg_mask("4034402c", "13:11", pa_vh_vbit)
        UARTc.write_reg_mask("40344038", "3:0", avss_hd1)
        UARTc.write_reg_mask("40344040", "12:10", dtmx_vh_vbit)
        UARTc.write_reg_mask("40344040", "9:7", dtmx_vlo_vbit)
        UARTc.write_reg_mask("40344040", "6:3", dtmx_dac_cscd_vbit)

        for dtmx_dac_cscd_vbit in range(0, 16, 2):
            UARTc.write_reg_mask("40344040", "6:3", dtmx_dac_cscd_vbit)

            UARTc.sendcmd("setch " + str(ch))
            time.sleep(2)

            # set cmp180
            CMPX.wlan_auto_peak_pwr()
            CMPX.wlan_meas_start()
            time.sleep(2)

            # measure evm and power
            ms_pwr = CMPX.wlan_meas_pwr()
            ms_evm = CMPX.wlan_meas_evm()
            CMPX.wlan_meas_abort()

            # read regs
            pa_vh_vbitx = UARTc.read_reg_bits("4034402c", "13:11")
            avss_hd1x = UARTc.read_reg_bits("40344038", "3:0")
            dtmx_vh_vbitx = UARTc.read_reg_bits("40344040", "12:10")
            dtmx_vlo_vbitx = UARTc.read_reg_bits("40344040", "9:7")
            dtmx_dac_cscd_vbitx = UARTc.read_reg_bits("40344040", "6:3")

            # write results
            results = "{},{},{},{},{},{},{},{}".format(ch, pa_vh_vbitx, avss_hd1x, dtmx_vh_vbitx, dtmx_vlo_vbitx,
                                                   dtmx_dac_cscd_vbitx, ms_pwr, ms_evm)
            CSVX.write_append_line(results)

            print(results)

    UARTc.sendcmd("settx 0")
    UARTc.close()

