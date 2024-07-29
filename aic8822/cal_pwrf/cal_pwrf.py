import os
import time
import math
import numpy as np

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from aic8822.pwr_sense.GlobalVar import *
from aic8822.msadc.msadc import *


class cal_pwrf:
    def __init__(self):
        self.UARTc = GX.get_value("UARTc")

    def pa_pwrsense_lb0_on(self):
        # loft en
        self.UARTc.write_reg_mask("403440A8", "20", 1)
        # loft vi mode
        self.UARTc.write_reg_mask("403440A8", "14", 1)
        # loft lpf mode
        self.UARTc.write_reg_mask("403440A8", "15", 1)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("403440A8", "13:11", 4)
        # test_enable lb0 pa
        self.UARTc.write_reg_mask("40344024", "18", 1)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)   #0: pwrsense #3: vl sense
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 3)

    def pa_pwrsense_lb0_off(self):
        # loft en
        self.UARTc.write_reg_mask("403440A8", "20", 0)
        # loft vi mode
        self.UARTc.write_reg_mask("403440A8", "14", 0)
        # loft lpf mode
        self.UARTc.write_reg_mask("403440A8", "15", 0)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("403440A8", "13:11", 4)
        # test_enable lb0 pa
        self.UARTc.write_reg_mask("40344024", "18", 0)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 0)

    def pa_pwrsense_hb0_on(self):
        # loft en
        self.UARTc.write_reg_mask("40344070", "14", 1)
        # loft vi mode
        self.UARTc.write_reg_mask("40344070", "8", 1)
        # loft lpf mode
        self.UARTc.write_reg_mask("40344070", "9", 1)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("40344070", "7:5", 4)
        # test_enable hb0 pa
        self.UARTc.write_reg_mask("40344024", "26", 1)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 3)

    def pa_pwrsense_hb0_off(self):
        # loft en
        self.UARTc.write_reg_mask("40344070", "14", 0)
        # loft vi mode
        self.UARTc.write_reg_mask("40344070", "8", 0)
        # loft lpf mode
        self.UARTc.write_reg_mask("40344070", "9", 0)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("40344070", "7:5", 4)
        # test_enable hb0 pa
        self.UARTc.write_reg_mask("40344024", "26", 0)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 0)

    def pa_pwrsense_lb1_on(self):
        # loft en
        self.UARTc.write_reg_mask("40344118", "19", 1)
        # loft vi mode
        self.UARTc.write_reg_mask("40344118", "13", 1)
        # loft lpf mode
        self.UARTc.write_reg_mask("40344118", "14", 1)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("40344118", "12:10", 4)
        # test_enable lb1 pa
        self.UARTc.write_reg_mask("40344024", "1", 1)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 3)

    def pa_pwrsense_lb1_off(self):
        # loft en
        self.UARTc.write_reg_mask("40344118", "19", 0)
        # loft vi mode
        self.UARTc.write_reg_mask("40344118", "13", 0)
        # loft lpf mode
        self.UARTc.write_reg_mask("40344118", "14", 0)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("40344118", "12:10", 4)
        # test_enable lb1 pa
        self.UARTc.write_reg_mask("40344024", "1", 0)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 0)

    def pa_pwrsense_hb1_on(self):
        # loft en
        self.UARTc.write_reg_mask("403440E4", "22", 1)
        # loft vi mode
        self.UARTc.write_reg_mask("403440E4", "16", 1)
        # loft lpf mode
        self.UARTc.write_reg_mask("403440E4", "17", 1)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("403440E4", "15:13", 4)
        # test_enable hb1 pa
        self.UARTc.write_reg_mask("40344024", "9", 1)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 3)

    def pa_pwrsense_hb1_off(self):
        # loft en
        self.UARTc.write_reg_mask("403440E4", "22", 0)
        # loft vi mode
        self.UARTc.write_reg_mask("403440E4", "16", 0)
        # loft lpf mode
        self.UARTc.write_reg_mask("403440E4", "17", 0)
        # loft mixer bias bit
        self.UARTc.write_reg_mask("403440E4", "15:13", 4)
        # test_enable hb1 pa
        self.UARTc.write_reg_mask("40344024", "9", 0)
        # test bit
        self.UARTc.write_reg_mask("40502018", "17:15", 0)
        # mode bit
        self.UARTc.write_reg_mask("40502018", "8:7", 0)

    def pa_pwrsense_on(self, ch=1, ANT="0"):
        if (ch<20) and (ANT=="0"):
            self.pa_pwrsense_lb0_on()
        elif (ch<20) and (ANT=="1"):
            self.pa_pwrsense_lb1_on()
        elif (ch>30) and (ANT=="0"):
            self.pa_pwrsense_hb0_on()
        elif (ch>30) and (ANT=="1"):
            self.pa_pwrsense_hb1_on()
        else:
            print("Input Error!!!")

    def pa_pwrsense_off(self, ch=1, ANT="0"):
        if (ch<20) and (ANT=="0"):
            self.pa_pwrsense_lb0_off()
        elif (ch<20) and (ANT=="1"):
            self.pa_pwrsense_lb1_off()
        elif (ch>30) and (ANT=="0"):
            self.pa_pwrsense_hb0_off()
        elif (ch>30) and (ANT=="1"):
            self.pa_pwrsense_hb1_off()
        else:
            print("Input Error!!!")

    def pa_gain_dr_off(self, ch=1, ANT="0"):
        if (ch < 20) and (ANT == "0"):
            self.UARTc.write_reg_mask("40344004", "13:12", 2)
        elif (ch < 20) and (ANT == "1"):
            self.UARTc.write_reg_mask("4034400C", "9:8", 2)
        elif (ch > 30) and (ANT == "0"):
            self.UARTc.write_reg_mask("40344000", "15:14", 2)
        elif (ch > 30) and (ANT == "1"):
            self.UARTc.write_reg_mask("40344008", "9:8", 2)
        else:
            print("Input Error!!!")

    def pa_gain_dr_release(self, ch = 1, ANT = "0"):
        if (ch < 20) and (ANT == "0"):
            self.UARTc.write_reg_mask("40344004", "13:12", 0)
        elif (ch < 20) and (ANT == "1"):
            self.UARTc.write_reg_mask("4034400C", "9:8", 0)
        elif (ch > 30) and (ANT == "0"):
            self.UARTc.write_reg_mask("40344000", "15:14", 0)
        elif (ch > 30) and (ANT == "1"):
            self.UARTc.write_reg_mask("40344008", "9:8", 0)
        else:
            print("Input Error!!!")


    def cal_pwrf_lb_ofdm(self, ant_sel="0", ch_gainmap_dict = {1: "966", 7: "96F", 13: "975"}):
        # CHGAINMAPDICT should match tx gain map, setpwr 15
        # CHGAINMAPDICT , CH: ANAINDEX+DIGINDEX

        # msadc init
        MSADCX = MSADC(clk_div=30, acc_mode=1, adc_id=1)

        # get ch ref
        ch_ref = 1

        # set init
        self.UARTc.sendcmd("setch {}".format(ch_ref))
        time.sleep(2)
        self.UARTc.sendcmd("pwrmm 1")
        self.UARTc.sendcmd("setpwr 15")
        self.UARTc.sendcmd("setrate 5 11")
        self.UARTc.sendcmd("setbw 1 1")
        self.UARTc.sendcmd("settx 1")
        self.UARTc.sendcmd("settx 0")

        # 2 open power sense
        self.pa_pwrsense_on(ch_ref, ant_sel)

        # 3 tone ant sel
        tone_ant_sel = "01"
        if ant_sel == "0":
            tone_ant_sel = "01"
        if ant_sel == "1":
            tone_ant_sel = "10"

        # measure power
        l_ch = []
        l_msadc_pwr = []
        for chx in ch_gainmap_dict.keys():
            # 1 init setting
            self.UARTc.sendcmd("setch {}".format(int(chx)))
            time.sleep(2)

            # 2 get ana index and dig index
            ana_index_hex = ch_gainmap_dict[chx][0]
            dig_index_hex = ch_gainmap_dict[chx][1:] + "0"

            # 4 measure opam offset
            self.UARTc.sendcmd("tone_on {} 4 {} {}".format(tone_ant_sel, "0", ana_index_hex))
            time.sleep(1)
            self.pa_gain_dr_off(chx, ant_sel)
            pwrofst_msadc = MSADCX.ms_portdc()
            self.UARTc.sendcmd("tone_off 11")
            print("MSADC PWR SENSE REF: {:.2f}".format(pwrofst_msadc))
            self.pa_gain_dr_release(chx, ant_sel)

            # 4 measure pwr
            # a, tone on
            tone_on_cmd = "tone_on {} 4 {} {}".format(tone_ant_sel, dig_index_hex, ana_index_hex)
            self.UARTc.sendcmd(tone_on_cmd)
            time.sleep(1)
            pwr_msadc_mw = MSADCX.ms_portdc() - pwrofst_msadc

            pwr_msadc_mw_cal = 0.00170*pwr_msadc_mw * pwr_msadc_mw + 0.8466*pwr_msadc_mw
            pwr_msadc_dbm_cal = 10.0 * math.log10(pwr_msadc_mw_cal)

            l_ch.append(chx)
            l_msadc_pwr.append(pwr_msadc_dbm_cal)

            #5 tone_off
            self.UARTc.sendcmd("tone_off 11")

        # pwr sense off
        self.pa_pwrsense_off(ch_ref, ant_sel)

        # pwr list
        print(l_msadc_pwr)

        # calculate offset
        pwr_median = np.median(l_msadc_pwr)
        l_offset = []
        for pwr in l_msadc_pwr:
            l_offset.append(round((pwr_median - pwr)*2.0))
        print([l_ch, l_offset])

        # gain_map + l_offset*0.5
        ch_offset_dict = {}
        i = 0
        for chx in l_ch:
            ch_offset_dict[chx] = l_offset[i]
            i = i + 1
        return ch_offset_dict


    def cal_pwrf_hb(self, ant_sel="0", ch_gainmap_dict = {42: "99A", 58: "998", 106: "994", 122: "996", 138: "996", 155: "996"}, CH42_CH58_OFFSET_dB=-1.5):
        # CHGAINMAPDICT , match setpwr 12
        # CHGAINMAPDICT , CH: ANAINDEX+DIGINDEX
        # OFSET_DB : Measure Power,  PWR_CH42/CH58 - PWR_CH106/CH122/CH138/CH155 = 1.5dB

        # msadc init
        MSADCX = MSADC(clk_div=30, acc_mode=1, adc_id=1)

        # get ch ref
        ch_ref = 42

        # set init
        self.UARTc.sendcmd("setch {}".format(ch_ref))
        time.sleep(2)
        self.UARTc.sendcmd("pwrmm 1")
        self.UARTc.sendcmd("setpwr 12")
        self.UARTc.sendcmd("setrate 5 11")
        self.UARTc.sendcmd("setbw 1 1")
        self.UARTc.sendcmd("settx 1")
        self.UARTc.sendcmd("settx 0")

        # 3 tone ant sel
        tone_ant_sel = "01"
        if ant_sel == "0":
            tone_ant_sel = "01"
        if ant_sel == "1":
            tone_ant_sel = "10"

        # measure power
        l_ch_42_58 = []
        l_msadc_pwr_42_58 = []
        l_ch_106_155 = []
        l_msadc_pwr_106_155 = []
        for chx in ch_gainmap_dict.keys():
            # 1 init setting
            self.UARTc.sendcmd("setch {}".format(int(chx)))
            time.sleep(2)

            # 2 get ana index and dig index
            ana_index_hex = ch_gainmap_dict[chx][0]
            dig_index_hex = ch_gainmap_dict[chx][1:] + "0"

            # 2 open power sense
            self.pa_pwrsense_on(chx, ant_sel)

            # 4 measure opam offset
            self.UARTc.sendcmd("tone_on {} 4 {} {}".format(tone_ant_sel, "0", ana_index_hex))
            time.sleep(1)
            self.pa_gain_dr_off(chx, ant_sel)
            pwrofst_msadc = MSADCX.ms_portdc()
            self.UARTc.sendcmd("tone_off 11")
            # print("MSADC PWR SENSE REF: {:.2f}".format(pwrofst_msadc))
            self.pa_gain_dr_release(chx, ant_sel)

            # 4 measure pwr
            # a, tone on
            tone_on_cmd = "tone_on {} 4 {} {}".format(tone_ant_sel, dig_index_hex, ana_index_hex)
            self.UARTc.sendcmd(tone_on_cmd)
            time.sleep(1)
            pwr_msadc_mw = MSADCX.ms_portdc() - pwrofst_msadc
            # print(pwr_msadc_mw)

            coef_dict = {42:  [4.4E-4, 8E-1, 1.5],
                         58:  [3.3E-4, 7E-1, 1.5],
                         106: [4.4E-4, 8E-1, 0],
                         122: [4.0E-4, 8E-1, 0],
                         138: [6.0E-4, 1.0, 0],
                         155: [5.0E-4, 1.0, 0]}

            # for chx
            # pwr_msadc_mw_cal = 0.00170*pwr_msadc_mw * pwr_msadc_mw + 0.8466*pwr_msadc_mw
            pwr_msadc_mw_cal = coef_dict[chx][0]*pwr_msadc_mw * pwr_msadc_mw + coef_dict[chx][1]*pwr_msadc_mw + coef_dict[chx][2]
            pwr_msadc_dbm_cal = 10.0 * math.log10(pwr_msadc_mw_cal)

            if chx <70:
                l_ch_42_58.append(chx)
                l_msadc_pwr_42_58.append(pwr_msadc_dbm_cal)
            elif chx < 170:
                l_ch_106_155.append(chx)
                l_msadc_pwr_106_155.append(pwr_msadc_dbm_cal)

            # tone off
            self.UARTc.sendcmd("tone_off 11")

        # power sense off
        self.pa_pwrsense_off(ch_ref, ant_sel)

        # pwr list
        print(l_ch_42_58+l_ch_106_155, l_msadc_pwr_42_58+l_msadc_pwr_106_155)

        # calculate offset ch106-ch155
        pwr_median_106_155 = np.median(l_msadc_pwr_106_155)
        print("CH106-CH155 Median Power = {} dBm".format(pwr_median_106_155))
        l_offset_106_155 = []
        for pwr in l_msadc_pwr_106_155:
            l_offset_106_155.append(round((pwr_median_106_155 - pwr)*2.0))
        # print([l_ch_106_155, l_offset_106_155])

        # calculate offset ch42-ch58
        if abs(l_msadc_pwr_42_58[0] - pwr_median_106_155) < abs(l_msadc_pwr_42_58[1] - pwr_median_106_155):
            pwr_median_42_58 = l_msadc_pwr_42_58[0]
        else:
            pwr_median_42_58 = l_msadc_pwr_42_58[1]
        print("CH42-CH58 Median Power = {} dBm".format(pwr_median_42_58))

        offset1 = []
        for pwr in l_msadc_pwr_42_58:
            offset1.append(round((pwr_median_42_58 - pwr)*2.0))
        l_offset_42_58 = offset1

        l_ch = l_ch_42_58 + l_ch_106_155
        l_offset = l_offset_42_58 + l_offset_106_155
        print([l_ch, l_offset])

        # gain_map + l_offset*0.5
        ch_offset_dict = {}
        i = 0
        for chx in l_ch:
            ch_offset_dict[chx] = l_offset[i]
            i = i + 1
        return ch_offset_dict


if __name__ == "__main__":
    UARTc = Uart(7)
    UARTc.open()
    GX.set_value("UARTc", UARTc)

    # cal_pwrf_lb("1")
    cal_pwrf_hb("0")

    UARTc.close()
