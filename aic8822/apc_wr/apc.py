### AIC8822 APC SET

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


def setapc_lb0(endpos, startpos, value, page):
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
        UARTc.write_reg_mask(reg_add1, "{}:{}".format(31, startpos), value%pow(2, 32 - startpos))
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos-32, 0), value >> (32 - startpos))
    elif (startpos > 31) and (endpos < 64):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos - 32, startpos - 32), value)
    elif (startpos < 64) and (endpos > 63):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(31, startpos-32), value%pow(2, 64-startpos))
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


def apc09_dr(page, index):
    UARTc.write_reg_mask("403441a4", "5:0", "9")  # table 0, index 9
    UARTc.write_reg_mask("403441a4", "6", "1")
    UARTc.write_reg_mask("403441a4", "7", "1")


def setapc_hb0(endpos, startpos, value, page):
    # start apc
    UARTc.sendcmd("w 403441d0 e")
    UARTc.sendcmd("w 403441b8 222")
    UARTc.sendcmd("w 403441b8 0")
    UARTc.sendcmd("w 403441d0 9")
    UARTc.sendcmd("w 403441b8 444")
    UARTc.sendcmd("w 403441b8 555")

    # edit apc value
    reg_add1 = aicNum(int(aicNum("0x403470b0").DEC) + int(page*256)).HEX
    reg_add2 = aicNum(int(aicNum("0x403470b4").DEC) + int(page*256)).HEX
    reg_add3 = aicNum(int(aicNum("0x403470b8").DEC) + int(page*256)).HEX
    if endpos < 32:
        UARTc.write_reg_mask(reg_add1, "{}:{}".format(endpos, startpos), value)
        print("{} {}:{} {}".format(reg_add1, endpos, startpos, value))
    elif (endpos > 31) and (startpos < 32):
        UARTc.write_reg_mask(reg_add1, "{}:{}".format(31, startpos), value%pow(2, 32 - startpos))
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos-32, 0), value >> (32 - startpos))
    elif (startpos > 31) and (endpos < 64):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(endpos - 32, startpos - 32), value)
    elif (startpos < 64) and (endpos > 63):
        UARTc.write_reg_mask(reg_add2, "{}:{}".format(31, startpos-32), value%pow(2, 64-startpos))
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


def apc0b_dr(page, index):
    UARTc.write_reg_mask("403441a4", "5:0", "11")  # table 0, index 9
    UARTc.write_reg_mask("403441a4", "6", "1")
    UARTc.write_reg_mask("403441a4", "7", "1")


def apc0b_release(page, index):
    UARTc.write_reg_mask("403441a4", "5:0", "0")  # table 0, index 9
    UARTc.write_reg_mask("403441a4", "6", "0")
    UARTc.write_reg_mask("403441a4", "7", "1")


def lb0_apc_sweep():
    UARTc = uart_open(7)

    CHIP_NO = "A4"

    ch = 7

    csv_path = "../AIC8822_WF_MEASURE_PWR_LB_20241202.csv"
    csvx = CSV(csv_path)

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    apc09_dr(0, 0)
    # [apc_end, apc_start, defvalue, regadd, ragpos]
    wf_dac0_vl_it_bit = ["dac0_it", 4, 0, 15, "40344124", "7:3"]
    wf_dac0_vl_ib_bit = ["dac0_ib", 9, 5, 19, "40344128", "21:17"]
    wf_lb0_tmx_cbit = ["tmx_c", 16, 13, 7, "40344084", "6:3"]
    wf_lb0_padrv_gbit = ["padrv_g", 25, 22, 1, "40344088", "15:12"]
    wf_lb0_padrv_cbit = ["padrv_c", 29, 26, 3, "40344088", "11:8"]
    wf_lb0_padrv_input_cbit = ["padrv_input_c", 32, 30, 7, "40344088", "7:5"]
    wf_lb0_pa_input_cbit = ["pa_input_c", 48, 46, 7, "40344098", "22:20"]
    wf_lb0_pa_gbit = ["pa_g", 52, 49, 13, "40344098", "19:16"]

    # apc_reg_list = [wf_dac0_vl_it_bit, wf_dac0_vl_ib_bit, wf_lb0_tmx_cbit, wf_lb0_padrv_gbit,
    #                wf_lb0_padrv_cbit, wf_lb0_padrv_input_cbit, wf_lb0_pa_input_cbit, wf_lb0_pa_gbit]

    #apc_reg_list = [wf_dac0_vl_it_bit, wf_dac0_vl_ib_bit, wf_lb0_tmx_cbit, wf_lb0_padrv_gbit,
    #               wf_lb0_padrv_cbit, wf_lb0_padrv_input_cbit, wf_lb0_pa_input_cbit, wf_lb0_pa_gbit]

    apc_reg_list = [wf_lb0_tmx_cbit, wf_lb0_padrv_cbit]

    for reg in apc_reg_list:
        # print(reg[0])
        for value in range(pow(2, reg[1] - reg[2] + 1)):
            # write apc
            setapc_lb0(reg[1], reg[2], value, 0)
            # read reg
            read_value = UARTc.read_reg_bits(reg[4], reg[5])

            # measure
            CMPX.wlan_auto_peak_pwr()
            CMPX.wlan_meas_start()
            time.sleep(2)

            ms_pwr = CMPX.wlan_meas_pwr()
            ms_evm = CMPX.wlan_meas_evm()

            res = "{}, {}, {}, {}, {}, {}".format(CHIP_NO, ch, reg[0], read_value, ms_pwr, ms_evm)
            print(res)

            csvx.write_append_line(res)

        # write def value
        setapc_lb0(reg[1], reg[2], reg[3], 0)


def hb0_apc_sweep():
    UARTc = uart_open(7)

    CHIP_NO = "A4"

    csv_path = "../AIC8822_WF_MEASURE_CAL_CBIT_HB_20241130.csv"
    csvx = CSV(csv_path)

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    # [apc_end, apc_start, defvalue, regadd, ragpos]
    wf_hb0_tmx_cbit = ["tmx_c", 17, 13, 9, "40344050", "11:7"]
    wf_hb0_padrv_cbit = ["padrv_c", 31, 27, 16, "40344054", "17:13"]

    apc_reg_list = [wf_hb0_tmx_cbit, wf_hb0_padrv_cbit]

    for ch in ["42", "58", "106", "122", "138", "155"]:
        CMPX.wlan_set_freq_by_ch(ch)
        UARTc.sendcmd("setch "+ch)
        time.sleep(2)
        apc0b_dr(0, 0)
        for reg in apc_reg_list:
            # print(reg[0])
            for value in range(pow(2, reg[1] - reg[2] + 1)):
                # write apc
                setapc_hb0(reg[1], reg[2], value, 0)
                # read reg
                read_value = UARTc.read_reg_bits(reg[4], reg[5])

                # measure
                CMPX.wlan_auto_peak_pwr()
                CMPX.wlan_meas_start()
                time.sleep(2)

                ms_pwr = CMPX.wlan_meas_pwr()
                ms_evm = CMPX.wlan_meas_evm()

                res = "{}, {}, {}, {}, {}, {}".format(CHIP_NO, ch, reg[0], read_value, ms_pwr, ms_evm)
                print(res)

                csvx.write_append_line(res)

            # write def value
            setapc_hb0(reg[1], reg[2], reg[3], 0)
        apc0b_release(0, 0)


if __name__ == "__main__":
    # hb0_apc_sweep()
    lb0_apc_sweep()