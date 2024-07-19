import os
import sys
import numpy as np
import time
from icbasic import *
from aic8822 import *
from aic8822.pwr_sense.GlobalVar import *
from icbasic.aicintf.uart import *


class MSADC:
    def __init__(self, clk_div=40, acc_mode=1, adc_id=0):
        self.UARTc = GX.get_value("UARTc")
        self.Mult = 1.0
        self.ClkDiv = clk_div
        if acc_mode == 0:
            self.Window = 256
            self.Denom = 8256
        elif acc_mode == 1:
            self.Window = 512
            self.Denom = 32896
        elif acc_mode == 2:
            self.Window = 1024
            self.Denom = 131328
        elif acc_mode == 3:
            self.Window = 4032
            self.Denom = 2033136
        else:
            raise "'acc_mode' is out of range"
        self.clkdivAddr = "40100038"
        self.vddSenAddr = "70001004"
        if adc_id == 0:  # pmu
            self.msAddr = "4010d004"
            self.winAddr = "4010d008"
            self.anaAddr = "4010d00c"
            self.roAddr = "4010d010"
        else:  # rf
            self.msAddr = "4010E004"
            self.winAddr = "4010E008"
            self.anaAddr = "4010E00C"
            self.roAddr = "4010E010"

    def basiconfig(self):
        self.UARTc.write_reg_mask(self.clkdivAddr, ["8", "7:0"], [1, self.ClkDiv])
        self.UARTc.write_reg_mask(self.winAddr, "27:16", self.Window)
        # print(self.winAddr, self.Window)
        self.UARTc.write_reg_mask(self.anaAddr, ["28:21", "18:12", "1"], [int('01010000', 2), int('1101010', 2), 0])

    def adconfig(self):
        self.UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [0, 1, 1, int('79', 16)],
                             "ts_mode/adc_ff_en/sdm_mode/others")

    def tsconfig(self):
        self.UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [1, 0, 0, int('8C', 16)],
                             "ts_mode/adc_ff_en/sdm_mode/others")

    def set_diff_mode(self):
        # mode 2
        self.UARTc.write_reg_mask(self.winAddr, "28", 1)
        self.UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 0])

    def set_se_p_mode(self):
        # single-ended positive port input
        self.UARTc.write_reg_mask(self.winAddr, "28", 0)
        self.UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 1])

    def set_se_n_mode(self):
        # single-ended positive port input
        self.UARTc.write_reg_mask(self.winAddr, "28", 0)
        self.UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 0])

    def set_selfcal_mode(self):
        # mode 3
        self.UARTc.write_reg_mask(self.winAddr, "28", 1)
        self.UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [1, 0])

    def self_calibration(self):
        self.basiconfig()
        self.adconfig()
        self.set_selfcal_mode()
        adc_ro = self.measure()
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult

    def input_sel_avdd33(self):  # it is vflash in aic8822
        self.UARTc.write_reg_mask(self.vddSenAddr, "15", 1)
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 3)
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 4.0

    def input_sel_avdd18(self):
        self.UARTc.write_reg_mask(self.vddSenAddr, "15", 1)
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 2)
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 2.0

    def input_sel_avdd13(self):
        self.UARTc.write_reg_mask(self.vddSenAddr, "15", 1)
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 1)
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 4.0 / 3.0

    def input_sel_vbat(self):
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 8)
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 5.5

    def input_sel_vtrc0(self):
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 4)
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vrefulpbuf(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 10)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_vcore(self):
        self.UARTc.write_reg_mask(self.winAddr, ["28", "3:0"], [0, 11])
        self.UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 1])
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio23_diff(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio01_diff(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio3(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_gpio2(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio1(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_gpio0(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_ts_pa(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 1)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_testport(self):
        self.UARTc.write_reg_mask(self.winAddr, "3:0", 0)
        self.set_se_p_mode()
        self.Mult = 1.0

    def vddsense_off(self):
        self.UARTc.write_reg_mask(self.vddSenAddr, "13:10", 0)
        self.Mult = 1

    def measure(self):
        self.UARTc.write_reg_mask(self.msAddr, "0", 1)  # start
        sleep_time = self.ClkDiv * 25E-9 * self.Window * 1.1
        time.sleep(sleep_time)
        return self.UARTc.read_reg(self.roAddr)

    def ms_volt(self):
        adc_ro = self.measure()
        # return unit V
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult / 1000.0

    # measure examples
    def ms_temp(self):
        self.basiconfig()
        self.tsconfig()
        adc_ro = self.measure()
        if self.Window == 256:
            coeff = 0.04
        elif self.Window == 512:
            coeff = 0.01
        elif self.Window == 1024:
            coeff = 0.00251
        else:
            coeff = 0.000162
        temp = coeff * int(adc_ro.split('x')[1], 16) - 283
        print("Temp  : {:4.0f} ".format(temp) + degree_sign + "C")
        return temp

    def ms_ts_conti(self, num=16):
        self.basiconfig()
        self.tsconfig()
        temp   = []
        if self.Window == 256:
            coeff = 0.04
        elif self.Window == 512:
            coeff = 0.01
        elif self.Window == 1024:
            coeff = 0.00251
        else:
            coeff = 0.000162
        for i in range(0, num):
            ro     = self.measure()
            value  = int(ro.split('x')[1], 16)
            temp_i = coeff * value - 283
            print("Temp  : {:4.0f} ".format(temp_i) + degree_sign + "C")
            temp.append(temp_i)
        return temp

    def ms_vbat(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vbat()
        v_vbat = self.ms_volt()
        self.vddsense_off()
        return v_vbat * 1000.0

    def ms_avdd33(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd33()
        v_avdd33 = self.ms_volt()
        self.vddsense_off()
        return v_avdd33 * 1000.0

    def ms_avdd18(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd18()
        v_avdd18 = self.ms_volt()
        self.vddsense_off()
        return v_avdd18 * 1000.0

    def ms_avdd13(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd13()
        v_avdd13 = self.ms_volt()
        self.vddsense_off()
        return v_avdd13 * 1000.0

    def ms_vrtc0(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vtrc0()
        v_vrtc0 = self.ms_volt()
        self.vddsense_off()
        return v_vrtc0 * 1000.0

    def ms_vrefulpbuf(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vrefulpbuf()
        v_vrefulpbuf = self.ms_volt()
        return v_vrefulpbuf * 1000.0

    def ms_vcore(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vcore()
        v_vcore = self.ms_volt()
        return v_vcore * 1000.0

    def ms_gpio23_diff(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio23_diff()
        v_vcore = self.ms_volt()
        return v_vcore * 1000.0

    def ms_gpio3(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio3()
        v_vcore = self.ms_volt()
        return v_vcore * 1000.0

    def ms_gpio2(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio2()
        v_vcore = self.ms_volt()
        return v_vcore * 1000.0

    def ms_portdc_config(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_testport()

    def ms_portdc(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_testport()
        v_portdc = self.ms_volt()
        return v_portdc * 1000.0

    def ms_dc_wfadc0(self):
        self.UARTc.write_reg_mask("40344028", "16", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        vreg_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        vref_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40344028", "16", 0)  # enable
        return [vreg_wfadc, vref_wfadc]

    def ms_dc_wfadc1(self):
        self.UARTc.write_reg_mask("40344028", "15", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        vreg_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        vref_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40344028", "15", 0)  # enable
        return [vreg_wfadc, vref_wfadc]

    def cal_dc_wfadc0(self):
        self.UARTc.write_reg_mask("40344028", "16", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        self.UARTc.write_reg_mask("40344154", "3:0", 8)  # adc0_vreg_vbit
        msb_vreg = 3
        for i in range(4):
            vreg_wfadc = self.ms_portdc()
            if vreg_wfadc > 970:
                self.UARTc.write_reg_mask("40344154", str(msb_vreg - i), 0)  # adc0_vreg_vbit
            if i < 3:
                self.UARTc.write_reg_mask("40344154", str(msb_vreg - 1 - i), 1)  # adc0_vreg_vbit
        vreg_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        self.UARTc.write_reg_mask("40344158", "19:15", 16)  # adc0_vref_vbit
        msb_vref = 19
        for i in range(5):
            vref_wfadc = self.ms_portdc()
            if vref_wfadc > 1010:
                self.UARTc.write_reg_mask("40344158", str(msb_vref - i), 0)  # adc0_vref_vbit
            if i < 4:
                self.UARTc.write_reg_mask("40344158", str(msb_vref - 1 - i), 1)  # adc0_vref_vbit
        vref_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40344028", "16", 0)  # enable
        return [vreg_wfadc, vref_wfadc]

    def cal_dc_wfadc1(self):
        self.UARTc.write_reg_mask("40344028", "15", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        self.UARTc.write_reg_mask("4034415c", "21:18", 8)  # adc1_vreg_vbit
        msb_vreg = 21
        for i in range(4):
            vreg_wfadc = self.ms_portdc()
            if vreg_wfadc > 970:
                self.UARTc.write_reg_mask("4034415c", str(msb_vreg - i), 0)  # adc1_vreg_vbit
            if i < 3:
                self.UARTc.write_reg_mask("4034415c", str(msb_vreg - 1 - i), 1)  # adc1_vreg_vbit
        vreg_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        self.UARTc.write_reg_mask("4034415c", "5:1", 16)  # adc1_vref_vbit
        msb_vref = 5
        for i in range(5):
            vref_wfadc = self.ms_portdc()
            if vref_wfadc > 1010:
                self.UARTc.write_reg_mask("4034415c", str(msb_vref - i), 0)  # adc1_vref_vbit
            if i < 4:
                self.UARTc.write_reg_mask("4034415c", str(msb_vref - 1 - i), 1)  # adc1_vref_vbit
        vref_wfadc = self.ms_portdc()
        self.UARTc.write_reg_mask("40344028", "15", 0)  # enable
        return [vreg_wfadc, vref_wfadc]

    def ms_dc_btadc(self, printEn=0):
        self.ms_portdc_config()
        self.UARTc.write_reg_mask("40622008", "13", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        # UARTc.write_reg_mask("40622024", " 7: 4", 8)  # adc1_vreg_vbit
        vreg_btadc = self.ms_volt()*1000
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        # UARTc.write_reg_mask("40622028", "23:19", 16)  # adc1_vref_vbit
        vref_btadc = self.ms_volt()*1000
        self.UARTc.write_reg_mask("40622008", "13", 0)  # enable
        if printEn == 1:
            print('vreg: {:5.1f}mV, vref: {:5.1f}mV'.format(vreg_btadc, vref_btadc))
        return [vreg_btadc, vref_btadc]

    def cal_dc_btadc(self, logOn=0):
        self.UARTc.write_reg_mask("40622008", "13", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 2)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 0)  # test_bit
        self.UARTc.write_reg_mask("40622024", " 7: 4", 8)  # adc_vreg_vbit
        self.ms_portdc_config()
        msb_vreg = 7
        for i in range(4):
            vreg_btadc = self.ms_volt() *1000
            if logOn == 1:
                print(str(i) + ": " + str(vreg_btadc))
            if vreg_btadc > 960:
                self.UARTc.write_reg_mask("40622024", str(msb_vreg - i), 0)  # adc_vreg_vbit
            if i < 3:
                self.UARTc.write_reg_mask("40622024", str(msb_vreg - 1 - i), 1)  # adc_vreg_vbit
        vreg_btadc = self.ms_volt() *1000
        if logOn == 1:
            bits = self.UARTc.read_reg_bits("40622024", "7:4")
            print(str(bits) + ": " + str(vreg_btadc))
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        self.UARTc.write_reg_mask("40622028", "23:19", 16)  # adc_vref_vbit
        msb_vref = 23
        for i in range(5):
            vref_btadc = self.ms_volt() *1000
            if logOn == 1:
                print(str(i) + ": " + str(vref_btadc))
            if vref_btadc > 960:
                self.UARTc.write_reg_mask("40622028", str(msb_vref - i), 0)  # adc_vref_vbit
            if i < 4:
                self.UARTc.write_reg_mask("40622028", str(msb_vref - 1 - i), 1)  # adc_vref_vbit
        vref_btadc = self.ms_volt() *1000
        if logOn == 1:
            bits = self.UARTc.read_reg_bits("40622028", "23:19")
            print(str(bits) + ": " + str(vref_btadc))
        self.UARTc.write_reg_mask("40622008", "13", 0)  # enable
        return [vreg_btadc, vref_btadc]

    def cal_dc_hb0_pa_opamp(self):
        self.UARTc.write_reg_mask("40344024", "26", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 3)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        self.UARTc.write_reg_mask("40344068", "19:14", int('100000', 2))  # hb0_pa_dc_cal_bit
        msb_vreg = 19
        for i in range(6):
            dcos0 = self.ms_portdc()
            print("DC offset: {: >3.1f} mV".format(dcos0))
            if dcos0 > 0:
                self.UARTc.write_reg_mask("40344068", str(msb_vreg - i), 0)  # adc1_vreg_vbit
            if i < 5:
                self.UARTc.write_reg_mask("40344068", str(msb_vreg - 1 - i), 1)  # adc1_vreg_vbit
        self.UARTc.write_reg_mask("40344024", "26", 0)  # enable

    def cal_dc_hb1_pa_opamp(self):
        self.UARTc.write_reg_mask("40344024", "26", 1)  # enable
        self.UARTc.write_reg_mask("40502018", " 8: 7", 3)  # test_mode
        self.UARTc.write_reg_mask("40502018", "17:15", 1)  # test_bit
        self.UARTc.write_reg_mask("40344024", "9", 1)  # enable
        self.UARTc.write_reg_mask("403440dc", "31:26", int('100000', 2))  # hb1_pa_dc_cal_bit
        msb_vreg = 31
        for i in range(6):
            dcos = self.ms_portdc()
            print("DC offset: {: >3.1f} mV".format(dcos))
            if dcos > 0:
                self.UARTc.write_reg_mask("403440dc", str(msb_vreg - i), 0)  # adc1_vreg_vbit
            if i < 5:
                self.UARTc.write_reg_mask("403440dc", str(msb_vreg - 1 - i), 1)  # adc1_vreg_vbit
        self.UARTc.write_reg_mask("40344024", "9", 0)  # enable


if __name__ == "__main__":
    UARTc = Uart(7)
    UARTc.open()
    UARTc.write_reg("40580018", 0)  # wf_rf_en (set it in btonly mode)
    UARTc.write_reg_bits("40506008", "18:17", 1)  # poff/on_wifi_core (set it in btonly mode)

    # UARTc.write_reg("4058001C", 0)  # bt_rf_en (de-bug of bt-pa in u02)
    # UARTc.write_reg_mask("40622000", " 3: 2", 3)  # de-bug of bt-pa in u02

    msadc0 = MSADC(clk_div=40, acc_mode=1, adc_id=0)
    # msadc0.ms_temp()

    # msadc1 = MSADC(clk_div=30, acc_mode=1, adc_id=1)
    # UARTc.write_reg_bits("40622000", "17:14", 15)  # pu_adc = 1
    # UARTc.write_reg_bits("40622004", " 7: 6", 3)   # pu_iref = 1
    # msadc1.cal_dc_btadc(1)
    # # msadc1.cal_dc_wfadc0()

    # msadc1 = MSADC(clk_div=20, acc_mode=1, adc_id=1)
    # msadc1.ms_dc_btadc(1)

    vcore  = msadc0.ms_vcore()
    # avdd18 = msadc0.ms_avdd18()
    # avdd13 = msadc0.ms_avdd13()
    # avdd33 = msadc0.ms_vbat()
    print("vcore  : {:6.1f} mV".format(vcore))
    # print("avdd13 : {:6.1f} mV".format(avdd13))
    # print("avdd18 : {:6.1f} mV".format(avdd18))
    # print("avdd33 : {:6.1f} mV".format(avdd33))

    # [vreg_adc0, vref_adc0] = msadc1.ms_dc_wfadc0()
    # [vreg_adc1, vref_adc1] = msadc1.ms_dc_wfadc1()
    # [vreg_adc0_cal, vref_adc0_cal] = msadc1.cal_dc_wfadc0()
    # [vreg_adc1_cal, vref_adc1_cal] = msadc1.cal_dc_wfadc1()
    # print("vref_adc0  : {:>6.1f} | {:>6.1f} mV".format(vref_adc0, vref_adc0_cal))
    # print("vref_adc1  : {:>6.1f} | {:>6.1f} mV".format(vref_adc1, vref_adc1_cal))
    # print("vreg_adc0  : {:>6.1f} | {:>6.1f} mV".format(vreg_adc0, vreg_adc0_cal))
    # print("vreg_adc1  : {:>6.1f} | {:>6.1f} mV".format(vreg_adc1, vreg_adc1_cal))
    #
    # UARTc.write_reg_mask("40622000", "17:14", 15)  # pu bt_adc
    # UARTc.write_reg_mask("40622004", "7:6", 3)  # pu_iref
    # UARTc.write_reg_mask("40622024", "19", 0)  # bt_adc_core_en
    # [vreg_btadc_cal, vref_btadc_cal] = msadc1.cal_dc_btadc()
    # print("vreg_btadc : {:>6.1f} mV".format(vreg_btadc_cal))
    # print("vref_btadc : {:>6.1f} mV".format(vref_btadc_cal))

    UARTc.close()