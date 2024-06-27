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
        UARTc.write_reg_mask("4010d00c", ["11","0"], [1, 0])

    def self_calibration(self):
        self.basiconfig()
        self.adconfig()
        self.set_selfcal_mode()
        self.input_sel_testport()
        adc_ro = self.measure()
        return (int(adc_ro.split('x')[1], 16)/self.Denom-1)*1214*self.Mult

    def input_sel_avdd33(self):  # mode 0
        UARTc.write_reg_mask("70001004", "13:10", 3)
        UARTc.write_reg_mask("4010d008", "3:0", 14)
        self.set_diff_mode()
        self.Mult = 4.0

    def input_sel_avdd18(self):
        UARTc.write_reg_mask("70001004", "13:10", 2)
        UARTc.write_reg_mask("4010d008", "3:0", 14)
        self.set_diff_mode()
        self.Mult = 2.0

    def input_sel_avdd13(self):
        UARTc.write_reg_mask("70001004", "13:10", 1)
        UARTc.write_reg_mask("4010d008", "3:0", 14)
        self.set_diff_mode()
        self.Mult = 4.0/3.0

    def input_sel_vbat(self):
        UARTc.write_reg_mask("70001004", ["13", "12", "11:10"], [1, 0, 0])
        UARTc.write_reg_mask("4010d008", "3:0", 14)
        self.set_diff_mode()
        self.Mult = 5.5

    def input_sel_vtrc0(self):
        UARTc.write_reg_mask("70001004", ["13", "12", "11:10"], [0, 1, 0])
        UARTc.write_reg_mask("4010d008", "3:0", 14)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vcore(self):
        UARTc.write_reg_mask("4010d008", ["28", "3:0"], [0, 10])
        UARTc.write_reg_mask("4010d00c", ["11","0"], [0, 1])
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_pasense(self):
        UARTc.write_reg_mask("4010d008", "3:0", 12)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_testport(self):
        UARTc.write_reg_mask("4010d008", "3:0", 0)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio23_diff(self):
        UARTc.write_reg_mask("4010d008", "3:0", 2)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio3(self):
        UARTc.write_reg_mask("4010d008", "3:0", 2)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio2(self):
        UARTc.write_reg_mask("4010d008", "3:0", 2)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_tsm1(self):
        UARTc.write_reg_mask("40344004", "16", 1, "wf_interface_ts_hub")
        UARTc.write_reg_mask("4010d008", "3:0", 1)
        self.set_diff_mode()
        self.Mult = 1.0

    def pa_cal_sel5u(self):
        UARTc.write_reg_mask("40344020", ["23", "22"], [1, 0])

    def pa_cal_selcore(self):
        UARTc.write_reg_mask("40344020", ["23", "22"], [1, 1])

    def pa_cal_off(self):
        UARTc.write_reg_mask("40344020", "23", 0)

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
        return 41 / 4112 * int(adc_ro.split('x')[1], 16) - 283

    def ms_temp_sense1(self):
        self.basiconfig()
        self.adconfig()
        self.set_diff_mode()
        self.input_sel_tsm1()
        adc_ro = self.measure()
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 596 - 260

    def ms_pa_current(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_pasense()
        self.pa_cal_sel5u()
        vout0 = self.ms_volt()
        self.pa_cal_selcore()
        vout1 = self.ms_volt()
        self.pa_cal_off()
        i_pa = vout1/vout0*93.68
        return i_pa

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

if __name__ == "__main__":

    uart_open(10)

    msadcx = MSADC()
    vcore = msadcx.ms_vcore()
    print("vcore  : " + str(vcore) + " mV")
    avdd13 = msadcx.ms_avdd13()
    print("avdd13 : " + str(avdd13) + " mV")
    avdd18 = msadcx.ms_avdd18()
    print("avdd18 : " + str(avdd18) + " mV")
    i_pa = msadcx.ms_pa_current()
    print("i_pa   : " + str(i_pa) + " mA")

    uart_close()