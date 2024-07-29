import os
import time
import math
import numpy as np

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from aic8822.pwr_sense.GlobalVar import *
global_create()
global GX
from aic8822.cal_pwrf.cal_pwrf import *
from aic8822.pwr_sense.csv import *


def cmp_ms_pwr_by_ch(l_ch=[1, 7, 13], setpwr = 15):

    setrate_ucmd = "setrate 5 7"
    setbw_ucmd = "setbw 1 1"
    setlen_ucmd = "setlen 20000"
    UARTc.sendcmd("settx 0")
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd(setrate_ucmd)
    UARTc.sendcmd(setbw_ucmd)
    UARTc.sendcmd(setlen_ucmd)
    rate = " ".join(setrate_ucmd.strip().split(" ")[1:])
    bw = " ".join(setbw_ucmd.strip().split(" ")[1:])
    len = " ".join(setbw_ucmd.strip().split(" ")[1:])

    if rate.strip().split(" ")[0] == "5":
        CMPX.wlan_set_standard("11ax")
    elif rate.strip().split(" ")[0] == "4":
        CMPX.wlan_set_standard("11ac")
    elif rate.strip().split(" ")[0] == "2":
        CMPX.wlan_set_standard("11n")

    if "0 0" in bw:
        CMPX.wlan_set_bandwidth("20")
    elif "1 1" in bw:
        CMPX.wlan_set_bandwidth("40")
    elif "2 2" in bw:
        CMPX.wlan_set_bandwidth("80")

    UARTc.sendcmd("setpwr {}".format(setpwr))

    ch_gainmap_dict = {}
    ch_pwr_dict = {}
    for chx in l_ch:
        setch_ucmd = "setch {}".format(chx)
        CMPX.wlan_set_freq_by_ch(chx)
        UARTc.sendcmd(setch_ucmd)
        time.sleep(2)

        UARTc.sendcmd("settx 1")
        CMPX.wlan_auto_peak_pwr()
        CMPX.wlan_meas_start()
        time.sleep(2)

        ms_pwr = CMPX.wlan_meas_pwr()
        ms_evm = CMPX.wlan_meas_evm()
        CMPX.wlan_meas_abort()

        l_reg = UARTc.read_reg("403422C8")
        ch_gainmap_dict[chx] = l_reg[-3:]
        ch_pwr_dict[chx] = ms_pwr

        results = "{},{},{},{}".format(chx, ms_pwr, ms_evm, l_reg[-3:])
        # CSVX.write_append_line(results)
        print(results)
    UARTc.sendcmd("settx 0")
    return ch_gainmap_dict, ch_pwr_dict


def test_lb_ant(ant_sel="0"):
    l_ch = [1, 7, 13]
    pwr = 15

    if ant_sel == "0":
        CMPX.wlan_set_route("RF1.8")
    elif ant_sel == "1":
        CMPX.wlan_set_route("RF2.8")

    ch_gainmap_dict, ch_mspwr_dict = cmp_ms_pwr_by_ch(l_ch, pwr)
    print(ch_gainmap_dict)

    # ch_gainmap_dict = {1: "97B", 7: "97E", 13: "97E"}
    ch_ofst_dict = cal_pwrf().cal_pwrf_lb(ant_sel, ch_gainmap_dict)
    print(ch_ofst_dict)

    ch_calpwr_dict = {}
    for chx in ch_mspwr_dict.keys():
        pwr_caled = float(ch_mspwr_dict[chx]) + 0.5* ch_ofst_dict[chx]
        ch_calpwr_dict[chx] = pwr_caled

    l_mspwr = []
    l_calpwr = []
    l_ofst = []
    for chx in ch_mspwr_dict.keys():
        l_mspwr.append(float(ch_mspwr_dict[chx]))
        l_ofst.append(ch_ofst_dict[chx])
        l_calpwr.append(ch_calpwr_dict[chx])

    max_delta_mspwr = max(l_mspwr) - min(l_mspwr)
    max_delta_calpwr = max(l_calpwr) - min(l_calpwr)

    print("PWR_MS:")
    print(ch_mspwr_dict)
    print("PWR_CALED:")
    print(ch_calpwr_dict)

    res = []
    for xx in l_mspwr + l_ofst + l_calpwr + [max_delta_mspwr, max_delta_calpwr]:
        res.append(str(xx))
    return res


def test_hb_ant(ant_sel="0"):
    l_ch = [42, 58, 106, 122, 138, 155]
    setpwr = 12

    if ant_sel == "0":
        CMPX.wlan_set_route("RF1.8")
    elif ant_sel == "1":
        CMPX.wlan_set_route("RF2.8")

    ch_gainmap_dict, ch_mspwr_dict = cmp_ms_pwr_by_ch(l_ch, setpwr)
    print(ch_gainmap_dict)
    print(ch_mspwr_dict)

    # ch_gainmap_dict = {1: "97B", 7: "97E", 13: "97E"}
    ch_ofst_dict = cal_pwrf().cal_pwrf_hb(ant_sel, ch_gainmap_dict)
    print(ch_ofst_dict)

    ch_calpwr_dict = {}
    for chx in ch_mspwr_dict.keys():
        pwr_caled = float(ch_mspwr_dict[chx]) + 0.5* ch_ofst_dict[chx]
        ch_calpwr_dict[chx] = pwr_caled

    l_mspwr = []
    l_calpwr = []
    l_ofst = []
    for chx in ch_mspwr_dict.keys():
        l_mspwr.append(float(ch_mspwr_dict[chx]))
        l_ofst.append(ch_ofst_dict[chx])
        l_calpwr.append(ch_calpwr_dict[chx])

    max_delta_mspwr = max(l_mspwr) - min(l_mspwr)
    max_delta_calpwr = max(l_calpwr) - min(l_calpwr)

    print("PWR_MS:")
    print(ch_mspwr_dict)
    print("PWR_CALED:")
    print(ch_calpwr_dict)

    res = []
    for xx in l_mspwr + l_ofst + l_calpwr + [max_delta_mspwr, max_delta_calpwr]:
        res.append(str(xx))
    return res


if __name__ == "__main__":

    UARTc = Uart(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    BOADINFO = "NO2"
    csv_path = "./data/20240729/test_hb.csv"
    # csv_header = "BOAEDNUM, ch1_ms, ch7_ms, ch13_ms, c cmp_pwr, cmp_evm, gain_index".format(BNUM)
    CSVX = CSV(csv_path)
    # CSVX.write_append_line("")

    GX.set_value("UARTc", UARTc)
    GX.set_value("CSVX", CSVX)
    GX.set_value("CMPX", CMPX)

    # lb cal
    # res_ant0 = test_lb_ant("0")
    # res_ant1 = test_lb_ant("1")

    # hb cal
    res_ant0 = test_hb_ant("0")
    res_ant1 = test_hb_ant("1")

    # hb cal

    CSVX.write_append_line(",".join([BOADINFO] + res_ant0 + ["NONE"] + res_ant1))

    # cal_pwrf_lb("0", ch_gainmap_dict_lb)

    # 1 ref