import os
import time
import math

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from aic8822.pwr_sense.GlobalVar import *
global_create()
from aic8822.msadc.msadc import *
from aic8822.pwr_sense.csv import *
global GX


def msadc_amam_by_dig_pwr(ch = 7, ant = 0, ana_index="9"):
    # 0 blk in ["lb0", "lb1", "hb0", ""hb1]
    #ana_index = "b"
    CSVX.write_append_line("ant, ch, pwr_dig, pwr_dig_dbm, pwr_cmp180_dbm")

    if int(ch) < 15:
        if ana_index == "b":
            ana_setpwr = "18"
        elif ana_index == "9":
            ana_setpwr = "14"
        else:
            ana_setpwr = "0"
    else:
        if ana_index == "d":
            ana_setpwr = "19"
        else:
            ana_setpwr = "19"

    if ant == 0:
        CMPX.fsq_set_route("RF1.8")
    elif ant == 1:
        CMPX.fsq_set_route("RF2.8")

    # 1 blk sel
    if (int(ch) < 15) and (ant == 0):
        ant_sel = "01"
    elif (int(ch) < 15) and (ant == 1):
        ant_sel = "10"
    elif (int(ch) > 15) and (ant == 0):
        ant_sel = "01"
    elif (int(ch) > 15) and (ant == 1):
        ant_sel = "10"
    else:
        ant_sel = "11"
        print("Input Error!!!")

    # 3 setch
    UARTc.sendcmd("setch {}".format(int(ch)))
    time.sleep(2)
    UARTc.sendcmd("setrate 5 11")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd("setpwr {}".format(ana_setpwr))
    UARTc.sendcmd("setbw 0 0")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")

    # 5 set cmp500
    CMPX.fsp_set_cfreq_by_ch(ch)

    # 7 measure pwr
    for dig_pwr in range(32, 4096, 32):  # 640
        dig_pwr_hex_str = hex(dig_pwr).split("0x")[-1]

        tone_on_cmd = "tone_on {} 4 {} {}".format(ant_sel, dig_pwr_hex_str, ana_index)
        UARTc.sendcmd(tone_on_cmd)
        time.sleep(0.5)
        CMPX.fsp_auto_enpwr()

        CMPX.fsp_on()
        pwr_dig = dig_pwr
        pwr_cmp180 = CMPX.fsp_peak_pwr()
        CMPX.fsp_off()

        pwr_dig_dbm = 20.0*math.log10(pwr_dig/4096)
        pwr_cmp180_dbm = pwr_cmp180

        pwr_result = "{},{},{},{:.2f},{:.2f}".format(ant, ch, pwr_dig, pwr_dig_dbm, pwr_cmp180_dbm)
        print(pwr_result)
        CSVX.write_append_line(pwr_result)

        UARTc.sendcmd("tone_off")
        UARTc.sendcmd("settx 0")
        time.sleep(2)


if __name__ == "__main__":
    csv_name = "./data/20240830/U05_NO1_ant0_amam_data_ch106_index_d_1138.csv"
    CSVX = CSV(csv_name)

    ANT = 0

    UARTc = Uart(11)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180(1)
    CMPX.open_tcp(host, port)

    GX.set_value("UARTc", UARTc)

    msadc_amam_by_dig_pwr(106, 0, "d")

    UARTc.close()