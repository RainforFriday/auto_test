import os
import sys
import numpy as np
import time
from aicbasic.AIC_C_CODE_LOG import *
from aicintf.uart import *
global UARTc
def uart_open(comport,baudrate=921600):
    global UARTc
    UARTc = Uart(comport)
    UARTc.set_baudrate(str(baudrate))
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()

def chip_id(logEn=1):
    projID = UARTc.read_reg_bits("40500000", "15:0")
    projID = format(projID, 'X')
    revID  = UARTc.read_reg_bits("40500000", "23:16")
    revID  = therm2dec(aicNum(revID).BIN)
    if logEn == 1:
        print("project : AIC" + projID)
        print("revision: {:d}".format(revID))
    return projID, revID

def log(str, logEn):
    if logEn == 1:
        print(str)

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
        self.clkdivAddr = "40100028"
        self.vddSenAddr = "70001004"
        self.msAddr     = "40102004"
        self.winAddr    = "40102008"
        self.anaAddr    = "4010200c"
        self.roAddr     = "40102010"

    def basiconfig(self):
        UARTc.write_reg_mask(self.clkdivAddr, ["8", "7:0"], [1, self.ClkDiv])
        UARTc.write_reg_mask(self.winAddr, "27:16", self.Window)
        UARTc.write_reg_mask(self.anaAddr, ["28:27", "26:25", "24:21", "18:15",   "14:12", "1"],
                                           [ 1,       1,       0,  int('1101', 2), 2,       0])

    def adconfig(self):
        UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [0, 1, 1, int('77', 16)],
                             "ts_mode/adc_ff_en/sdm_mode/others")

    def tsconfig(self):
        UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [1, 0, 0, int('8C', 16)],
                             "ts_mode/adc_ff_en/sdm_mode/others")

    def set_diff_mode(self):
        UARTc.write_reg_mask(self.winAddr, "28", 1)
        UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 0])

    def set_se_p_mode(self):
        # single-ended positive port input
        UARTc.write_reg_mask(self.winAddr, "28", 0)
        UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 1])

    def set_se_n_mode(self):
        # single-ended positive port input
        UARTc.write_reg_mask(self.winAddr, "28", 0)
        UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 0])

    def set_selfcal_mode(self):
        # mode 3
        UARTc.write_reg_mask(self.winAddr, "28", 1)
        UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [1, 0])

    def self_calibration(self):
        self.basiconfig()
        self.adconfig()
        self.set_selfcal_mode()
        adc_ro = self.measure()
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult

    def input_sel_avdd18(self):
        UARTc.write_reg_mask(self.vddSenAddr, "   13", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "   12", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "11:10", 3)
        UARTc.write_reg_mask(self.winAddr, "3:0", 15)
        self.set_diff_mode()
        self.Mult = 3.005

    def input_sel_vio18ulp(self):
        UARTc.write_reg_mask(self.vddSenAddr, "   13", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "   12", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "11:10", 2)
        UARTc.write_reg_mask(self.winAddr,    " 3: 0", 15)
        self.set_diff_mode()
        self.Mult = 2.004

    def input_sel_avdd13(self):
        UARTc.write_reg_mask(self.vddSenAddr, "   13", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "   12", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "11:10", 1)
        UARTc.write_reg_mask(self.winAddr,    " 3: 0", 15)
        self.set_diff_mode()
        self.Mult = 1.672

    def input_sel_vbat(self):
        UARTc.write_reg_mask(self.vddSenAddr, "   13", 1)
        UARTc.write_reg_mask(self.vddSenAddr, "   12", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "11:10", 0)
        UARTc.write_reg_mask(self.winAddr   , " 3: 0", 15)
        self.set_diff_mode()
        self.Mult = 5.46

    def input_sel_vtrc0(self):
        UARTc.write_reg_mask(self.vddSenAddr, "   13", 0)
        UARTc.write_reg_mask(self.vddSenAddr, "   12", 1)
        UARTc.write_reg_mask(self.vddSenAddr, "11:10", 0)
        UARTc.write_reg_mask(self.winAddr,    " 3: 0", 15)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vtrc1(self):
        UARTc.write_reg_mask(self.winAddr,    " 3: 0",  9)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_vtrc1_irdrop(self):
        UARTc.write_reg_mask(self.winAddr,    " 3: 0", 14)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vrefulpbuf(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 10)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_vcore_irdrop(self):
        UARTc.write_reg_mask(self.winAddr,    " 3: 0", 8)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_vcore(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 11)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio23_diff(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio3(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_gpio2(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_testport(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 0)
        self.set_diff_mode()
        self.Mult = 1.0

    def vddsense_off(self):
        UARTc.write_reg_mask(self.vddSenAddr, "13:10", 0)
        self.Mult = 1

    def measure(self):
        UARTc.write_reg_mask(self.msAddr, "0", 1)  # start
        sleep_time = self.ClkDiv * 25E-9 * self.Window * 1.1
        time.sleep(sleep_time)
        return UARTc.read_reg(self.roAddr)

    def ms_volt(self):
        adc_ro = self.measure()
        # return unit V
        return (int(adc_ro.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult / 1000.0

    # measure examples
    def ms_temp(self, logEn=0):
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
        if logEn==1: printT(temp)
        return temp

    def testmux(self, testmode=0, testbit=0):
        UARTc.write_reg_mask("40502008", "17:16", testmode)
        UARTc.write_reg_mask("40502008", "15:13", testbit)

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

    def ms_vio18ulp(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vio18ulp()
        v_vio18ulp = self.ms_volt()
        self.vddsense_off()
        return v_vio18ulp * 1000.0

    def ms_avdd18(self, logEn=0):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd18()
        v_avdd18 = self.ms_volt()
        self.vddsense_off()
        if logEn==1:
            printV("avdd18", v_avdd18*1000)
        return v_avdd18 * 1000.0

    def ms_avdd13(self, logEn=0):
        self.basiconfig()
        self.adconfig()
        self.input_sel_avdd13()
        v_avdd13 = self.ms_volt()
        self.vddsense_off()
        if logEn==1:
            printV("avddrf", v_avdd13*1000)
        return v_avdd13 * 1000.0

    def ms_vcore(self, logEn=0):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vcore()
        v_vcore = self.ms_volt()
        if logEn==1:
            printV("vcore", v_vcore*1000)
        return v_vcore * 1000.0

    def ms_vrtc0(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vtrc0()
        v_vrtc0 = self.ms_volt()
        self.vddsense_off()
        return v_vrtc0 * 1000.0

    def ms_vrtc1(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vtrc1()
        v_vrtc1 = self.ms_volt()
        return v_vrtc1 * 1000.0

    def ms_vtrc1_irdrop(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vtrc1_irdrop()
        v_vtrc1_irdrop = self.ms_volt()
        return v_vtrc1_irdrop * 1000.0

    def ms_vcore_irdrop(self):
        self.basiconfig()
        self.adconfig()
        self.set_selfcal_mode()
        vos = self.ms_volt()
        self.input_sel_vcore_irdrop()
        UARTc.write_reg_mask("70001040", "30", 1)  # ldo_vcore08_curdet_mode
        v_vtrc1_irdrop = self.ms_volt() - vos
        UARTc.write_reg_mask("70001040", "30", 0)  # ldo_vcore08_curdet_mode
        return v_vtrc1_irdrop * 1000.0

    def ms_vrefulpbuf(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vrefulpbuf()
        v_vrefulpbuf = self.ms_volt()
        return v_vrefulpbuf * 1000.0

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

    def ms_portdc(self, logEn=0):
        self.basiconfig()
        self.adconfig()
        self.input_sel_testport()
        v_portdc = self.ms_volt()
        log("portDC            : {:.2f}mV".format(v_portdc*1000), logEn)
        return v_portdc * 1000.0

    def cal_dc_wfadc(self, logEn=0):
        wfadc_reg = "40344064"
        wfadc_ref = "40344068"
        log("--> cal: dc_wfadc", logEn)
        self.te_wf_adc(1)
        ## --> vreg <--
        self.testmux(2, 0)
        UARTc.write_reg_mask(wfadc_reg, "16:13", 8)  # adc_vreg_vbit
        msb_vreg = 16
        for i in range(4):
            vreg_wfadc = self.ms_portdc()
            log("{:d}: {:.2f}mV".format(i, vreg_wfadc), logEn)
            if vreg_wfadc > 960:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vreg - i), 0)  # adc_vreg_vbit
            if i < 3:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vreg - 1 - i), 1)  # adc_vreg_vbit
        vreg_wfadc = self.ms_portdc()
        bits = UARTc.read_reg_bits(wfadc_reg, "16:13")
        log("Locked: {:d} -- {:.2f}mV".format(bits, vreg_wfadc), logEn)
        ## --> vref <--
        self.testmux(2, 1)
        UARTc.write_reg_mask(wfadc_ref, "17:13", 16)  # adc_vref_vbit
        msb_vref = 17
        for i in range(5):
            vref_wfadc = self.ms_portdc()
            log("{:d}: {:.2f}mV".format(i, vref_wfadc), logEn)
            if vref_wfadc > 960:
                UARTc.write_reg_mask(wfadc_ref, str(msb_vref - i), 0)  # adc_vref_vbit
            if i < 4:
                UARTc.write_reg_mask(wfadc_ref, str(msb_vref - 1 - i), 1)  # adc_vref_vbit
        vref_wfadc = self.ms_portdc()
        bits = UARTc.read_reg_bits(wfadc_ref, "17:13")
        log("Locked: {:d} -- {:.2f}mV".format(bits, vref_wfadc), logEn)
        ##
        self.te_wf_adc(0)
        return [vreg_wfadc, vref_wfadc]

    def ms_idc_wfpa(self, id_pa=0, logEn=0):
        wfpa_regAddr = "40344020"
        # log("--> ms: hb_pa_idc", logEn)
        self.ms_portdc_config()
        self.te_wf_pa(1)
        self.testmux(3, 0)
        UARTc.write_reg_mask(wfpa_regAddr, "   19", 1)  # isense_en
        UARTc.write_reg_mask(wfpa_regAddr, "16:14", 4)  # isense_rbit
        vdc_pa = 0
        if id_pa == 1:  # PA
            UARTc.write_reg_mask(wfpa_regAddr, "18:17", 1)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            log("WF_LB_PA: {:.2f}mV".format(vdc_pa), logEn)
        elif id_pa == 0:  # dtmx
            UARTc.write_reg_mask(wfpa_regAddr, "18:17", 0)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            log("WF_HB_PA: {:.2f}mV".format(vdc_pa), logEn)
        UARTc.write_reg_mask(wfpa_regAddr, "   19", 0)  # isense_en
        self.te_wf_pa(1)
        return vdc_pa

    def te_wf_tia(self, en=0):
        UARTc.write_reg_mask("40344004", " 8", en)

    def te_wf_rxflt(self, en=0):
        UARTc.write_reg_mask("40344004", " 5", en)

    def te_wf_adc(self, en=0):
        UARTc.write_reg_mask("40344004", " 4", en)

    def te_wf_vco(self, en=0):
        UARTc.write_reg_mask("40344004", " 6", en)

    def te_wf_rfpll(self, en=0):
        UARTc.write_reg_mask("40344004", " 7", en)

    def te_wf_dtmx(self, en=0):
        UARTc.write_reg_mask("40344004", "13", en)

    def te_wf_pa(self, en=0):
        UARTc.write_reg_mask("40344004", "10", en)


if __name__ == "__main__":
    UARTc = Uart(3)
    UARTc.open()

    msadc0 = MSADC(clk_div=40, acc_mode=1)
    msadc0.ms_temp(1)

    UARTc.close()