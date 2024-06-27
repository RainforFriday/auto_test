import os
import sys
import numpy
import time
from aicintf.uart import *
from aicintf.com import *
from aicbasic.AIC_C_CODE_LOG import *


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


class MSADC:
    def __init__(self, clk_div=40, acc_mode=1):
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

    def basiconfig(self):
        UARTc.write_reg_mask("40100038", ["8", "7:0"], [1, self.ClkDiv])
        UARTc.write_reg_mask("4010d008", "27:16", self.Window)
        UARTc.write_reg_mask("4010d00c", ["28:21", "18:12", "1"], [int('01010000', 2), int('1101010', 2), 0])

    def adconfig(self):
        UARTc.write_reg_mask("4010d00c", ["20", "19", "10", "9:2"], [0, 1, 1, int('79', 16)], "ts_mode/adc_ff_en/sdm_mode/others")

    def tsconfig(self):
        UARTc.write_reg_mask("4010d00c", ["20", "19", "10", "9:2"], [1, 0, 0, int('8C', 16)], "ts_mode/adc_ff_en/sdm_mode/others")

    def set_diff_mode(self):
        # mode 2
        UARTc.write_reg_mask("4010d008", "28", 1)
        UARTc.write_reg_mask("4010d00c", ["11", "0"], [0, 0])

    def set_se_p_mode(self):
        # single-ended positive port input
        UARTc.write_reg_mask("4010d008", "28", 0)
        UARTc.write_reg_mask("4010d00c", ["11", "0"], [0, 1])

    def set_se_n_mode(self):
        # single-ended positive port input
        UARTc.write_reg_mask("4010d008", "28", 0)
        UARTc.write_reg_mask("4010d00c", ["11", "0"], [0, 0])

    def set_selfcal_mode(self):
        #mode 3
        UARTc.write_reg_mask("4010d008", "28", 1)
        UARTc.write_reg_mask("4010d00c", ["11", "0"], [1, 0])

    def self_calibration(self):
        self.basiconfig()
        self.adconfig()
        self.set_selfcal_mode()
        adc_ro = self.measure()
        return (int(adc_ro.split('x')[1], 16)/self.Denom-1)*1214*self.Mult

    def input_sel_avdd33(self):  # mode 0
        UARTc.write_reg_mask("70001004", "13:10", 3)
        UARTc.write_reg_mask("4010d008", "3:0", 15)
        self.set_diff_mode()
        self.Mult = 4.0

    def input_sel_avdd18(self):
        UARTc.write_reg_mask("70001004", "13:10", 2)
        UARTc.write_reg_mask("4010d008", "3:0", 15)
        self.set_diff_mode()
        self.Mult = 2.0

    def input_sel_avdd13(self):
        UARTc.write_reg_mask("70001004", "13:10", 1)
        UARTc.write_reg_mask("4010d008", "3:0", 15)
        self.set_diff_mode()
        self.Mult = 4.0/3.0

    def input_sel_vbat(self):
        UARTc.write_reg_mask("70001004", "13:10", 8)
        UARTc.write_reg_mask("4010d008", "3:0", 15)
        self.set_diff_mode()
        self.Mult = 5.5

    def input_sel_vtrc0(self):
        UARTc.write_reg_mask("70001004", "13:10", 4)
        UARTc.write_reg_mask("4010d008", "3:0", 15)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vrefulpbuf(self):
        UARTc.write_reg_mask("4010d008", "3:0", 10)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_vcore(self):
        UARTc.write_reg_mask("4010d008", ["28", "3:0"], [0, 11])
        UARTc.write_reg_mask("4010d00c", ["11","0"], [0, 1])
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_isense(self):
        UARTc.write_reg_mask("4010d008", "3:0", 13)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio23_diff(self):
        UARTc.write_reg_mask("4010d008", "3:0", 3)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio3(self):
        UARTc.write_reg_mask("4010d008", "3:0", 3)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio2(self):
        UARTc.write_reg_mask("4010d008", "3:0", 3)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_ts_pa(self):
        UARTc.write_reg_mask("4010d008", "3:0", 1)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_testport(self):
        UARTc.write_reg_mask("4010d008", "3:0", 0)
        self.set_se_p_mode()
        self.Mult = 1.0

    def ts_pa24g_on(self):
        UARTc.write_reg_mask("40344008", "27", 1, "wf_pu_ts_hub")
        UARTc.write_reg_mask("40344064", ["21:18", "17:16"], [2, 2])

    def ts_pa5g_on(self):
        UARTc.write_reg_mask("40344008", "27", 1, "wf_pu_ts_hub")
        UARTc.write_reg_mask("40344064", ["21:18", "17:16"], [4, 2])

    def ts_pa_off(self):
        UARTc.write_reg_mask("40344008", "27", 0, "wf_pu_ts_hub")

    def lna_cal_on(self):
        UARTc.write_reg_mask("40622038", "4", 1)

    def lna_cal_off(self):
        UARTc.write_reg_mask("40622038", "4", 0)

    def pa5g_cal_sel5u(self):
        UARTc.write_reg_mask("4034403c", "1:0", 3)

    def pa5g_cal_selcore(self):
        UARTc.write_reg_mask("4034403c", "1:0", 2)

    def pa5g_cal_off(self):
        UARTc.write_reg_mask("4034403c", "1", 0)

    def pa24g_cal_sel5u(self):
        UARTc.write_reg_mask("40344040", "29", 1)
        UARTc.write_reg_mask("4034403c", "0", 1)

    def pa24g_cal_selcore(self):
        UARTc.write_reg_mask("40344040", "29", 1)
        UARTc.write_reg_mask("4034403c", "0", 0)

    def pa24g_cal_off(self):
        UARTc.write_reg_mask("40344040", "29", 0)

    def vddsense_off(self):
        UARTc.write_reg_mask("70001004", "13:10", 0)
        self.Mult = 1

    def measure(self):
        UARTc.write_reg_mask("4010d004", "0", 1)  # start
        sleep_time = self.ClkDiv*25E-9*self.Window*1.1
        time.sleep(sleep_time)
        return UARTc.read_reg("4010d010")

    def ms_volt(self):
        adc_ro = self.measure()
        # return unit V
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult/1000.0

    # measure examples
    def ms_temp_sense0(self):
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
        return temp

    def ms_ts0_conti(self, num=16):
        self.basiconfig()
        self.tsconfig()
        adc_ro = []
        for i in range(0, num):
            ro = self.measure()
            adc_ro.append(int(ro.split('x')[1], 16))
        if self.Window == 256:
            coeff = 0.04
        elif self.Window == 512:
            coeff = 0.01
        elif self.Window == 1024:
            coeff = 0.00251
        else:
            coeff = 0.000162
        temp = []
        for i in range(0, num):
            temp.append(coeff * adc_ro[i] - 283)
        return temp

    def ms_ts_pa24g(self):
        self.basiconfig()
        self.adconfig()
        self.ts_pa24g_on()
        self.input_sel_ts_pa()
        volt = self.ms_volt()
        self.ts_pa_off()
        return volt*547.9 - 275.6

    def ms_ts_pa5g(self):
        self.basiconfig()
        self.adconfig()
        self.ts_pa5g_on()
        self.input_sel_ts_pa()
        volt = self.ms_volt()
        self.ts_pa_off()
        return volt*547.9 - 275.6

    def ms_ts_pa5g_conti(self, num=16):
        self.basiconfig()
        self.adconfig()
        self.ts_pa5g_on()
        self.input_sel_ts_pa()
        temp = []
        for i in range(0, num):
            ts = 547.9 * self.ms_volt() - 275.6
            temp.append(ts)
        self.ts_pa_off()
        return temp

    def ms_pa5g_current(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_isense()
        self.pa5g_cal_sel5u()
        vout0 = self.ms_volt()
        self.pa5g_cal_selcore()
        vout1 = self.ms_volt()
        self.pa5g_cal_off()
        i_pa = vout1/vout0*522
        return vout0*1000

    def ms_pa24g_current(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_isense()
        self.pa24g_cal_sel5u()
        vout0 = self.ms_volt()
        self.pa24g_cal_selcore()
        vout1 = self.ms_volt()
        self.pa24g_cal_off()
        i_pa = vout1/vout0*522
        return vout1*1000

    def ms_lna_current(self):
        self.basiconfig()
        self.adconfig()
        vout0 = self.self_calibration()
        self.input_sel_isense()
        self.lna_cal_on()
        vout1 = self.ms_volt()*1000
        # self.lna_cal_off()
        i_lna = (vout1-vout0)/5.4
        return i_lna

    def ms_vbat(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vbat()
        v_vbat = self.ms_volt()
        self.vddsense_off()
        return v_vbat*1000.0

    def ms_avdd33(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd33()
        v_avdd33 = self.ms_volt()
        self.vddsense_off()
        return v_avdd33*1000.0

    def ms_avdd18(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd18()
        v_avdd18 = self.ms_volt()
        self.vddsense_off()
        return v_avdd18*1000.0

    def ms_avdd13(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd13()
        v_avdd13 = self.ms_volt()
        self.vddsense_off()
        return v_avdd13*1000.0

    def ms_vrtc0(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vtrc0()
        v_vrtc0 = self.ms_volt()
        self.vddsense_off()
        return v_vrtc0*1000.0

    def ms_vrefulpbuf(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vrefulpbuf()
        v_vrefulpbuf = self.ms_volt()
        return v_vrefulpbuf*1000.0

    def ms_vcore(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vcore()
        v_vcore = self.ms_volt()
        return v_vcore*1000.0

    def ms_gpio23_diff(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio23_diff()
        v_vcore = self.ms_volt()
        return v_vcore*1000.0

    def ms_gpio3(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio3()
        v_vcore = self.ms_volt()
        return v_vcore*1000.0

    def ms_gpio2(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_gpio2()
        v_vcore = self.ms_volt()
        return v_vcore*1000.0

    def ms_portdc(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_testport()
        v_portdc = self.ms_volt()
        return v_portdc*1000.0

    def ms_wfadcvref(self):
        UARTc.write_reg_mask("4034400c", "19", 1)
        UARTc.write_reg_mask("40344008", "2:0", 1)
        vref_wfadc = self.ms_portdc()
        UARTc.write_reg_mask("4034400c", "19", 0)
        return vref_wfadc

if __name__ == "__main__":

    UARTc = uart_open(7)

    msadcx = MSADC()
    UARTc.write_reg_mask("40344088", "22:20", 7)

    msadcx.input_sel_testport()

    # pa_test_enable_open
    UARTc.write_reg_mask("4034400c", "25", 1)

    # test_bit, lb_vl
    UARTc.write_reg_mask("40344008", "2:0", 2)
    vl = msadcx.ms_portdc()

    # test_bit, lb_vm
    UARTc.write_reg_mask("40344008", "2:0", 3)
    vm = msadcx.ms_portdc()

    print("Vl : " + str(vl) + "mV\n")
    print("Vm : " + str(vm*3.0) + "mV\n")

    UARTc.write_reg_mask("4034400c", "25", 0)
    UARTc.write_reg_mask("40344088", "22:20", 0)


    uart_close()