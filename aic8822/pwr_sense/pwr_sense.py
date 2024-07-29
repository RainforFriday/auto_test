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


def pa_pwrsense_lb0_on():
    # loft en
    UARTc.write_reg_mask("403440A8", "20", 1)
    # loft vi mode
    UARTc.write_reg_mask("403440A8", "14", 1)
    # loft lpf mode
    UARTc.write_reg_mask("403440A8", "15", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440A8", "13:11", 4)
    # test_enable lb0 pa
    UARTc.write_reg_mask("40344024", "18", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)   #0: pwrsense #3: vl sense
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)


def pa_pwrsense_lb0_off():
    # loft en
    UARTc.write_reg_mask("403440A8", "20", 0)
    # loft vi mode
    UARTc.write_reg_mask("403440A8", "14", 0)
    # loft lpf mode
    UARTc.write_reg_mask("403440A8", "15", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440A8", "13:11", 4)
    # test_enable lb0 pa
    UARTc.write_reg_mask("40344024", "18", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)


def pa_pwrsense_hb0_on():
    # loft en
    UARTc.write_reg_mask("40344070", "14", 1)
    # loft vi mode
    UARTc.write_reg_mask("40344070", "8", 1)
    # loft lpf mode
    UARTc.write_reg_mask("40344070", "9", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344070", "7:5", 4)
    # test_enable hb0 pa
    UARTc.write_reg_mask("40344024", "26", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)


def pa_pwrsense_hb0_off():
    # loft en
    UARTc.write_reg_mask("40344070", "14", 0)
    # loft vi mode
    UARTc.write_reg_mask("40344070", "8", 0)
    # loft lpf mode
    UARTc.write_reg_mask("40344070", "9", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344070", "7:5", 4)
    # test_enable hb0 pa
    UARTc.write_reg_mask("40344024", "26", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)


def pa_pwrsense_lb1_on():
    # loft en
    UARTc.write_reg_mask("40344118", "19", 1)
    # loft vi mode
    UARTc.write_reg_mask("40344118", "13", 1)
    # loft lpf mode
    UARTc.write_reg_mask("40344118", "14", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344118", "12:10", 4)
    # test_enable lb1 pa
    UARTc.write_reg_mask("40344024", "1", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)


def pa_pwrsense_lb1_off():
    # loft en
    UARTc.write_reg_mask("40344118", "19", 0)
    # loft vi mode
    UARTc.write_reg_mask("40344118", "13", 0)
    # loft lpf mode
    UARTc.write_reg_mask("40344118", "14", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344118", "12:10", 4)
    # test_enable lb1 pa
    UARTc.write_reg_mask("40344024", "1", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)


def pa_pwrsense_hb1_on():
    # loft en
    UARTc.write_reg_mask("403440E4", "22", 1)
    # loft vi mode
    UARTc.write_reg_mask("403440E4", "16", 1)
    # loft lpf mode
    UARTc.write_reg_mask("403440E4", "17", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440E4", "15:13", 4)
    # test_enable hb1 pa
    UARTc.write_reg_mask("40344024", "9", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)


def pa_pwrsense_hb1_off():
    # loft en
    UARTc.write_reg_mask("403440E4", "22", 0)
    # loft vi mode
    UARTc.write_reg_mask("403440E4", "16", 0)
    # loft lpf mode
    UARTc.write_reg_mask("403440E4", "17", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440E4", "15:13", 4)
    # test_enable hb1 pa
    UARTc.write_reg_mask("40344024", "9", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)


def pa_pwrsen_on(blk = "lb0"):
    if blk == "lb0":
        pa_pwrsense_lb0_on()
    elif blk == "lb1":
        pa_pwrsense_lb1_on()
    elif blk == "hb0":
        pa_pwrsense_hb0_on()
    elif blk == "hb1":
        pa_pwrsense_hb1_on()
    else:
        print("Input Error!!!")


def pa_pwrsen_off(blk = "lb0"):
    if blk == "lb0":
        pa_pwrsense_lb0_off()
    elif blk == "lb1":
        pa_pwrsense_lb1_off()
    elif blk == "hb0":
        pa_pwrsense_hb0_off()
    elif blk == "hb1":
        pa_pwrsense_hb1_off()
    else:
        print("Input Error!!!")


def pa_gain_dr_off(blk = "lb0"):
    if blk == "lb0":
        UARTc.write_reg_mask("40344004", "13:12", 2)
    elif blk == "lb1":
        UARTc.write_reg_mask("4034400C", "9:8", 2)
    elif blk == "hb0":
        UARTc.write_reg_mask("40344000", "15:14", 2)
    elif blk == "hb1":
        UARTc.write_reg_mask("40344008", "9:8", 2)
    else:
        print("Input Error!!!")


def pa_gain_dr_release(blk = "lb0"):
    if blk == "lb0":
        UARTc.write_reg_mask("40344004", "13:12", 0)
    elif blk == "lb1":
        UARTc.write_reg_mask("4034400C", "9:8", 0)
    elif blk == "hb0":
        UARTc.write_reg_mask("40344000", "15:14", 0)
    elif blk == "hb1":
        UARTc.write_reg_mask("40344008", "9:8", 0)
    else:
        print("Input Error!!!")


def msadc_pwr_sense_by_dig_pwr(ch = 1, ant = 0):
    # 0 blk in ["lb0", "lb1", "hb0", ""hb1]
    ana_index = "9"
    CSVX.write_append_line("ant, ch, pwr_dig, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw")

    if ant == 0:
        CMPX.fsq_set_route("RF1.8")
    elif ant == 1:
        CMPX.fsq_set_route("RF2.8")

    # 1 blk sel
    if (int(ch) < 15) and (ant == 0):
        blk = "lb0"
        ant_sel = "01"
    elif (int(ch) < 15) and (ant == 1):
        blk = "lb1"
        ant_sel = "10"
    elif (int(ch) > 15) and (ant == 0):
        blk = "hb0"
        ant_sel = "01"
    elif (int(ch) > 15) and (ant == 1):
        blk = "hb1"
        ant_sel = "10"
    else:
        blk = "lb0"
        ant_sel = "11"
        print("Input Error!!!")

    # 2 msadc init
    MSADCX = MSADC(clk_div=30, acc_mode=1, adc_id=1)

    # 3 setch
    UARTc.sendcmd("setch {}".format(int(ch)))
    time.sleep(2)
    UARTc.sendcmd("setrate 5 11")
    UARTc.sendcmd("setbw 1 1")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")


    # 4 open pa pwr sense
    pa_pwrsen_on(blk)

    # 5 set cmp500
    CMPX.fsp_set_cfreq_by_ch(ch)

    # 6 get ref
    UARTc.sendcmd("tone_on {} 4 {} {}".format(ant_sel, "0", ana_index))
    time.sleep(1)
    # UARTc.write_reg_mask("40344004", "13:12", 2)
    pa_gain_dr_off(blk)
    pwrref_msadc = MSADCX.ms_portdc()
    UARTc.sendcmd("tone_off 11")
    print("MSADC PWR SENSE REF: {:.2f}".format(pwrref_msadc))
    pa_gain_dr_release(blk)
    # UARTc.write_reg_mask("40344004", "13:12", 0)

    # 7 measure pwr
    for dig_pwr in range(640, 4096, 64):  # 640
        dig_pwr_hex_str = hex(dig_pwr).split("0x")[-1]

        tone_on_cmd = "tone_on {} 4 {} {}".format(ant_sel, dig_pwr_hex_str, ana_index)
        # print(tone_on_cmd)
        UARTc.sendcmd(tone_on_cmd)
        time.sleep(1)
        CMPX.fsp_auto_enpwr()

        CMPX.fsp_on()
        pwr_dig = dig_pwr
        pwr_msadc = MSADCX.ms_portdc() - pwrref_msadc
        pwr_cmp180 = CMPX.fsp_peak_pwr()
        # freq_cmp180 = CMPX.fsp_peak_freq()
        CMPX.fsp_off()

        pwr_dig_dbm = 20.0*math.log10(pwr_dig)
        pwr_msadc_dbm = 10.0*math.log10(pwr_msadc)
        pwr_cmp180_dbm = pwr_cmp180

        pwr_msadc_mw = pwr_msadc
        pwr_cmp180_mw = pow(10.0, pwr_cmp180_dbm/10.0)

        # for 2.4G band
        if ch < 15:
            pwr_msadc_mw_fix_coeff = 0.00107*pwr_msadc_mw + 0.8466
            pwr_msadc_mw_cal = pwr_msadc_mw*pwr_msadc_mw_fix_coeff
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        # for 5G band
        if (ch > 30) and (ch < 170):
            pwr_msadc_mw_cal = pwr_msadc_mw*1.547 - 0.6
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        pwr_result = "{},{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}".format(ant, ch, pwr_dig, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw)
        print(pwr_result)
        CSVX.write_append_line(pwr_result)

        UARTc.sendcmd("tone_off 11")

    # 7 close pwr sense
    pa_pwrsen_off(blk)


def msadc_pwr_sense_by_ch(dig_pwr_dec = 640, ant = 0, l_ch = None):
    # 0 blk in ["lb0", "lb1", "hb0", ""hb1]
    ana_index = "b"
    CSVX.write_append_line("ch, pwr_dig, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw, pwr_msadc_mw_cal, pwr_msadc_dbm_cal")

    # msadc init
    MSADCX = MSADC(clk_div=30, acc_mode=1, adc_id=1)

    # 7 measure pwr
    for chx in l_ch:
        # 1 blk sel
        if (int(chx) < 15) and (ant == 0):
            blk = "lb0"
            ant_sel = "01"
        elif (int(chx) < 15) and (ant == 1):
            blk = "lb1"
            ant_sel = "10"
        elif (int(chx) > 15) and (ant == 0):
            blk = "hb0"
            ant_sel = "01"
        elif (int(chx) > 15) and (ant == 1):
            blk = "hb1"
            ant_sel = "10"
        else:
            blk = "lb0"
            ant_sel = "11"
            print("Input Error!!!")

        # 2 setch
        UARTc.sendcmd("setch {}".format(int(chx)))
        time.sleep(2)
        UARTc.sendcmd("setrate 5 11")
        UARTc.sendcmd("setbw 1 1")
        UARTc.sendcmd("settx 1")
        UARTc.sendcmd("settx 0")

        # 3 open pa pwr sense
        pa_pwrsen_on(blk)

        # 4 set cmp500
        CMPX.fsp_set_cfreq_by_ch(chx)

        # 5 get ref
        UARTc.sendcmd("tone_on {} 4 {} {}".format(ant_sel, "0", ana_index))
        time.sleep(1)
        # UARTc.write_reg_mask("40344004", "13:12", 2)
        pa_gain_dr_off(blk)
        pwrref_msadc = MSADCX.ms_portdc()
        UARTc.sendcmd("tone_off 11")
        print("MSADC PWR SENSE REF: {:.2f}".format(pwrref_msadc))
        pa_gain_dr_release(blk)

        dig_pwr_hex_str = hex(dig_pwr_dec).split("0x")[-1]

        tone_on_cmd = "tone_on {} 4 {} {}".format(ant_sel, dig_pwr_hex_str, ana_index)
        # print(tone_on_cmd)
        UARTc.sendcmd(tone_on_cmd)
        time.sleep(2)
        CMPX.fsp_auto_enpwr()

        CMPX.fsp_on()
        pwr_dig = dig_pwr_dec
        pwr_msadc = MSADCX.ms_portdc() - pwrref_msadc
        pwr_cmp180 = CMPX.fsp_peak_pwr()
        # freq_cmp180 = CMPX.fsp_peak_freq()
        CMPX.fsp_off()

        pwr_dig_dbm = 20.0*math.log10(pwr_dig)
        pwr_msadc_dbm = 10.0*math.log10(pwr_msadc)
        pwr_cmp180_dbm = pwr_cmp180

        pwr_msadc_mw = pwr_msadc
        pwr_cmp180_mw = pow(10.0, pwr_cmp180_dbm/10.0)

        pwr_msadc_mw_cal = "NONE"
        pwr_msadc_dbm_cal = "NONE"

        # for 2.4G band
        if chx < 15:
            pwr_msadc_mw_fix_coeff = 0.00107*pwr_msadc_mw + 0.8466
            pwr_msadc_mw_cal = pwr_msadc_mw*pwr_msadc_mw_fix_coeff
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        # for 5G band
        if (chx > 30) and (chx < 170):
            # function 1
            # pwr_msadc_mw_cal = pwr_msadc_mw*1.547 - 0.6
            # function 2
            pwr_msadc_mw_cal = 9.2E-4*pwr_msadc_mw*pwr_msadc_mw + 1.434*pwr_msadc_mw + 1.707
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        pwr_result = "{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}".format(chx, pwr_dig, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw, pwr_msadc_mw_cal, pwr_msadc_dbm_cal)
        print(pwr_result)
        CSVX.write_append_line(pwr_result)

        UARTc.sendcmd("tone_off 11")

        # 7 close pwr sense
        pa_pwrsen_off(blk)


def msadc_pwr_sense_by_ch_digpwr(ch_digpwr_dict = {}, ant = 0, ana_index = "c"):
    # 0 blk in ["lb0", "lb1", "hb0", ""hb1]
    CSVX.write_append_line("ch, pwr_dig, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw, pwr_msadc_mw_cal, pwr_msadc_dbm_cal")

    # msadc init
    MSADCX = MSADC(clk_div=30, acc_mode=1, adc_id=1)

    # 7 measure pwr
    for chx in ch_digpwr_dict.keys():
        # 1 blk sel
        if (int(chx) < 15) and (ant == 0):
            blk = "lb0"
            ant_sel = "01"
        elif (int(chx) < 15) and (ant == 1):
            blk = "lb1"
            ant_sel = "10"
        elif (int(chx) > 15) and (ant == 0):
            blk = "hb0"
            ant_sel = "01"
        elif (int(chx) > 15) and (ant == 1):
            blk = "hb1"
            ant_sel = "10"
        else:
            blk = "lb0"
            ant_sel = "11"
            print("Input Error!!!")

        # 2 setch
        UARTc.sendcmd("setch {}".format(int(chx)))
        time.sleep(2)
        UARTc.sendcmd("setrate 5 11")
        UARTc.sendcmd("setbw 1 1")
        UARTc.sendcmd("settx 1")
        UARTc.sendcmd("settx 0")

        # 3 open pa pwr sense
        pa_pwrsen_on(blk)

        # 4 set cmp500
        CMPX.fsp_set_cfreq_by_ch(chx)

        # 5 get ref
        UARTc.sendcmd("tone_on {} 4 {} {}".format(ant_sel, "0", ana_index))
        time.sleep(1)
        # UARTc.write_reg_mask("40344004", "13:12", 2)
        pa_gain_dr_off(blk)
        pwrref_msadc = MSADCX.ms_portdc()
        UARTc.sendcmd("tone_off 11")
        print("MSADC PWR SENSE REF: {:.2f}".format(pwrref_msadc))
        pa_gain_dr_release(blk)

        dig_pwr_hex_str = ch_digpwr_dict[chx] + "0"

        tone_on_cmd = "tone_on {} 4 {} {}".format(ant_sel, dig_pwr_hex_str, ana_index)
        # print(tone_on_cmd)
        UARTc.sendcmd(tone_on_cmd)
        time.sleep(2)
        CMPX.fsp_auto_enpwr()

        CMPX.fsp_on()

        dig_pwr_dec = int(dig_pwr_hex_str, 16)
        pwr_dig = dig_pwr_dec
        pwr_msadc = MSADCX.ms_portdc() - pwrref_msadc
        pwr_cmp180 = CMPX.fsp_peak_pwr()
        # freq_cmp180 = CMPX.fsp_peak_freq()
        CMPX.fsp_off()

        pwr_dig_dbm = 20.0*math.log10(pwr_dig)
        pwr_msadc_dbm = 10.0*math.log10(pwr_msadc)
        pwr_cmp180_dbm = pwr_cmp180

        pwr_msadc_mw = pwr_msadc
        pwr_cmp180_mw = pow(10.0, pwr_cmp180_dbm/10.0)

        pwr_msadc_mw_cal = "NONE"
        pwr_msadc_dbm_cal = "NONE"

        # for 2.4G band
        if chx < 15:
            pwr_msadc_mw_fix_coeff = 0.00107*pwr_msadc_mw + 0.8466
            pwr_msadc_mw_cal = pwr_msadc_mw*pwr_msadc_mw_fix_coeff
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        # for 5G band
        if (chx > 30) and (chx < 170):
            # function 1
            # pwr_msadc_mw_cal = pwr_msadc_mw*1.547 - 0.6
            # function 2
            pwr_msadc_mw_cal = 9.2E-4*pwr_msadc_mw*pwr_msadc_mw + 1.434*pwr_msadc_mw + 1.707
            pwr_msadc_dbm_cal = 10.0*math.log10(pwr_msadc_mw_cal)

        pwr_result = "{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}".format(chx, dig_pwr_hex_str, pwr_dig_dbm, pwr_msadc_dbm, pwr_cmp180_dbm, pwr_msadc_mw, pwr_cmp180_mw, pwr_msadc_mw_cal, pwr_msadc_dbm_cal)
        print(pwr_result)
        CSVX.write_append_line(pwr_result)

        UARTc.sendcmd("tone_off 11")

        # 7 close pwr sense
        pa_pwrsen_off(blk)


if __name__ == "__main__":
    csv_name = "./data/20240726/NREF_pwr_sense_data_20240726_1646.csv"
    CSVX = CSV(csv_name)

    ANT = 0

    UARTc = Uart(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180(1)
    CMPX.open_tcp(host, port)

    GX.set_value("UARTc", UARTc)

    MSADCX = MSADC(clk_div=40, acc_mode=1, adc_id=0)

    ch_list_lb = [1, 7, 13]
    ch_list_hb = [42, 58, 106, 122, 138, 155]

    for chx in ch_list_hb:
        msadc_pwr_sense_by_dig_pwr(chx, 0)
        msadc_pwr_sense_by_dig_pwr(chx, 1)


    # for dig_pwr in range(640, 2000, 192):
    #    msadc_pwr_sense_by_ch(dig_pwr, ANT, ch_list_hb)

    # ch_dig_pwr_dict = {42: "9D", 58: "9C", 106: "96", 122: "97", 138: "97", 155: "97"}
    # ch_dig_pwr_dict = {1:"66", 7:"6F", 13:"75"}
    # msadc_pwr_sense_by_ch_digpwr(ch_dig_pwr_dict, 0, "9")

    UARTc.close()