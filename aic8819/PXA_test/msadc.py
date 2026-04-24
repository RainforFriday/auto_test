# from aic8822 import *
# from aic8819.uart_config import UARTc
from AIC_TEST.icbasic.aicintf.uart import *
from toolkit.ApcReg import *
# from aic8819.aic8819_tunnertest.aic8819_tunner_txtest.apc8819 import *

# from pyintf.uart import *


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc

def uart_close():
    UARTc.close()


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
        self.clkdivAddr = "40100038"
        self.vddSenAddr = "70001004"
        self.msAddr = "4010d004"
        self.winAddr = "4010d008"
        self.anaAddr = "4010d00c"
        self.roAddr = "4010d010"

    def basiconfig(self):
        UARTc.write_reg_mask(self.clkdivAddr, ["8", "7:0"], [1, self.ClkDiv])
        UARTc.write_reg_mask(self.winAddr, "27:16", self.Window)
        UARTc.write_reg_mask(self.anaAddr, ["28:27", "26:25", "24:21", "18:15",   "14:12", "1"],
                                           [ 1,       1,       0,  int('1101', 2), 2,       0])

    def adconfig(self):
        UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [0, 1, 1, int('79', 16)],
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
        UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio01_diff(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_diff_mode()
        self.Mult = 1.0

    def input_sel_gpio3(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_gpio2(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 2)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_gpio1(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_n_mode()
        self.Mult = 1.0

    def input_sel_gpio0(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 3)
        self.set_se_p_mode()
        self.Mult = 1.0

    def input_sel_ts_pa(self):
        UARTc.write_reg_mask(self.winAddr, "3:0", 1)
        self.set_diff_mode()
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
        log("Temp  : {:4.1f} ".format(temp) + degree_sign + "C", logEn)
        # print("Temp  : {:4.0f} ".format(temp) + degree_sign + "C")
        return temp

    def testmux(self, testmode=0, testbit=0):
        UARTc.write_reg_mask("40502010", " 8: 7", testmode)
        UARTc.write_reg_mask("40502010", " 2: 0", testbit)

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

    def ms_vcore(self):
        self.basiconfig()
        self.adconfig()
        self.input_sel_vcore()
        v_vcore = self.ms_volt()
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
        UARTc.write_reg_mask("70001044", "30", 1)  # ldo_vcore08_curdet_mode
        v_vtrc1_irdrop = self.ms_volt() - vos
        UARTc.write_reg_mask("70001044", "30", 0)  # ldo_vcore08_curdet_mode
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

    def portdc_mode(self, mode=3):
        UARTc.write_reg_mask("40502010", " 8:7", mode)  # test_mode

    def portdc_bit(self, bit=0):
        UARTc.write_reg_mask("40502010", "2:0", bit)  # test_bit

    def cal_dc_wfadc(self, logEn=0):
        wfadc_reg = "40344088"
        log("--> cal: dc_wfadc0", logEn)
        self.te_wf_adc(1)
        self.testmux(2, 0)
        UARTc.write_reg_mask(wfadc_reg, "21:18", 8)  # adc0_vreg_vbit
        msb_vreg = 21
        for i in range(4):
            vreg_wfadc = self.ms_portdc()
            log("{:d}: {:.2f}mV".format(i, vreg_wfadc), logEn)
            if vreg_wfadc > 960:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vreg - i), 0)  # adc0_vreg_vbit
            if i < 3:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vreg - 1 - i), 1)  # adc0_vreg_vbit
        vreg_wfadc = self.ms_portdc()
        bits = UARTc.read_reg_bits(wfadc_reg, "21:18")
        log("Locked: {:d} -- {:.2f}mV".format(bits, vreg_wfadc), logEn)
        #
        self.testmux(2, 1)
        UARTc.write_reg_mask(wfadc_reg, "5:1", 16)  # adc_vref_vbit
        msb_vref = 5
        for i in range(5):
            vref_wfadc = self.ms_portdc()
            log("{:d}: {:.2f}mV".format(i, vref_wfadc), logEn)
            if vref_wfadc > 960:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vref - i), 0)  # adc_vref_vbit
            if i < 4:
                UARTc.write_reg_mask(wfadc_reg, str(msb_vref - 1 - i), 1)  # adc_vref_vbit
        vref_wfadc = self.ms_portdc()
        bits = UARTc.read_reg_bits(wfadc_reg, "5:1")
        log("Locked: {:d} -- {:.2f}mV".format(bits, vref_wfadc), logEn)
        self.te_wf_adc(0)
        return [vreg_wfadc, vref_wfadc]

    def cal_dc_btadc(self, logEn=0):
        btadc_vreg_regAddr = "4062201c"
        btadc_vcal_regAddr = "40622018"
        log("--> cal: dc_btadc", logEn)
        self.te_bt_sdmadc(1)
        self.testmux(2,6)
        UARTc.write_reg_mask(btadc_vreg_regAddr, "11:8", 8)  # adc_vreg_vbit
        self.ms_portdc_config()
        msb_vreg = 11
        for i in range(4):
            vreg_btadc = self.ms_volt() *1000
            log("{:d}: {:.2f}mV".format(i, vreg_btadc), logEn)
            if vreg_btadc > 960:
                UARTc.write_reg_mask(btadc_vreg_regAddr, str(msb_vreg - i), 0)  # adc_vreg_vbit
                # log(">", logEn)
            if i < 3:
                UARTc.write_reg_mask(btadc_vreg_regAddr, str(msb_vreg - 1 - i), 1)  # adc_vreg_vbit
                # log("<", logEn)
        vreg_btadc = self.ms_volt() *1000
        bits = UARTc.read_reg_bits(btadc_vreg_regAddr, "11:8")
        log("Locked: {:d} -- {:.2f}mV".format(bits, vreg_btadc), logEn)
        # #
        self.testmux(1,6)
        UARTc.write_reg_mask(btadc_vcal_regAddr, "3:0", 8)  # adc_vcal_vbit
        msb_vref = 3
        for i in range(4):
            vrefsrc_btadc = abs(self.ms_volt() *1000)
            log("{:d}: {:.2f}mV".format(i, vrefsrc_btadc), logEn)
            if vrefsrc_btadc > 650:
                UARTc.write_reg_mask(btadc_vcal_regAddr, str(msb_vref - i), 0)  # adc_vcal_vbit
            if i < 3:
                UARTc.write_reg_mask(btadc_vcal_regAddr, str(msb_vref - 1 - i), 1)  # adc_vcal_vbit
        vrefsrc_btadc = abs(self.ms_volt() *1000)
        bits = UARTc.read_reg_bits(btadc_vcal_regAddr, "3:0")
        self.testmux(1, 5)
        vref_btadc = abs(self.ms_volt() * 1000)
        log("Locked: {:d} -- {:.2f}mV {:.2f}mV".format(bits, vrefsrc_btadc, vref_btadc), logEn)
        self.te_bt_sdmadc(0)
        return [vreg_btadc, vrefsrc_btadc]

    def ms_idc_wfpa(self, id_pa=0, logEn=0):
        wfpa_regAddr = "40344044"
        # log("--> ms: hb_pa_idc", logEn)
        self.ms_portdc_config()
        self.te_wf_pa(1)
        self.testmux(3, 0)
        UARTc.write_reg_mask(wfpa_regAddr, "   12", 1)  # isense_en
        UARTc.write_reg_mask(wfpa_regAddr, "11: 9", 4)  # isense_rbit
        vdc_pa = 0
        if id_pa == 2:
            UARTc.write_reg_mask(wfpa_regAddr, " 8: 7", 2)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            log("BT_PA   : {:.2f}mV".format(vdc_pa), logEn)
        elif id_pa == 1:
            UARTc.write_reg_mask(wfpa_regAddr, " 8: 7", 1)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            log("WF_LB_PA: {:.2f}mV".format(vdc_pa), logEn)
        elif id_pa == 0:
            UARTc.write_reg_mask(wfpa_regAddr, " 8: 7", 0)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            log("WF_HB_PA: {:.2f}mV".format(vdc_pa), logEn)
        UARTc.write_reg_mask(wfpa_regAddr, "   12", 0)  # isense_en
        self.te_wf_pa(1)
        return vdc_pa

    def te_bt_sdmadc(self, en=0):
        UARTc.write_reg_mask("40622004", "   10", en)

    def te_wf_rxflt(en=0):
        UARTc.write_reg_mask("4034400c", "   29", en)

    def te_wf_adc(self, en=0):
        UARTc.write_reg_mask("4034400c", "   28", en)

    def te_wf_pa(self, en=0):
        UARTc.write_reg_mask("40344008", "    5", en)

    def ms_wf_current(self, id_pa=0):
        wfpa_regAddr = "40344044"
        # log("--> ms: hb_pa_idc", logEn)
        self.ms_portdc_config()
        self.te_wf_pa(1)
        self.testmux(3, 0)
        UARTc.write_reg_mask(wfpa_regAddr, "   12", 1)  # isense_en
        UARTc.write_reg_mask(wfpa_regAddr, "11: 9", 4)  # isense_rbit
        vdc_pa = 0
        if id_pa == 1:
            UARTc.write_reg_mask(wfpa_regAddr, " 8: 7", 1)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            #log("WF_LB_PA: {:.2f}mV".format(vdc_pa), logEn)
        elif id_pa == 0:
            UARTc.write_reg_mask(wfpa_regAddr, " 8: 7", 0)  # isense_input_sel
            vdc_pa = self.ms_volt() *1000
            #log("WF_HB_PA: {:.2f}mV".format(vdc_pa), logEn)
        UARTc.write_reg_mask(wfpa_regAddr, "   12", 0)  # isense_en
        self.te_wf_pa(0)
        return vdc_pa




if __name__ == "__main__":

    # UARTc.open()
    UARTc=uart_open(3)
    msadc0 = MSADC(clk_div=40, acc_mode=1)
    # msadc0.ms_temp(1)
    # msadc0.portdc_bit(6)
    # msadc0.portdc_mode(2)
    # for i in range(2):
    #     aa=msadc0.ms_portdc()
    #     print(aa)
    # msadc0.portdc_bit(6)
    # msadc0.portdc_mode(1)
    # for i in range(2):
    #     dd = msadc0.ms_portdc()
    #     print(dd)
    # msadc0.portdc_bit(2)
    # msadc0.portdc_mode(2)
    # for i in range(2):
    #     bb=msadc0.ms_portdc()
    #     print(bb*3)
    # msadc0.portdc_bit(1)
    # msadc0.portdc_mode(2)
    # for i in range(2):
    #     cc=msadc0.ms_portdc()
    #     print(cc*2)
    #bb = msadc0.ms_wf_current(0)
    #print(bb)

    msadc0.portdc_bit(7)
    msadc0.portdc_mode(2)
    for i in range(1):
        aa=msadc0.ms_portdc()
        print(f'Vl: {aa}')

    msadc0.portdc_bit(1)
    msadc0.portdc_mode(2)
    for i in range(1):
        dd = msadc0.ms_portdc()*2
        print(f'Vm: {dd}')

    msadc0.portdc_bit(2)
    msadc0.portdc_mode(2)
    for i in range(1):
        dd = msadc0.ms_portdc() * 3
        print(f'Vh: {dd}')




    #
    # REG_HIGH = "0"
    # # REG_LOW = "40348560"
    # REG_LOW = "40344004"
    # apc_reg = ApcReg(UARTc,REG_LOW,REG_HIGH)
    #
    #
    # value1 = apc_reg.rapc(31, 30)
    # print(f'31~30_1: {value1}')
    #
    # cc=apc_reg.read_reg(apc_reg.REG_LOW)
    # print(f'read_reg: {hex(cc)}')
    #
    #
    # apc_reg.wapc(31, 30, 3)  # 0 or 8191
    #
    # value2 = apc_reg.rapc(31, 30)
    # print(f'31~30_2: {value2}')
    #
    # dd = apc_reg.read_reg(apc_reg.REG_LOW)
    # print(f'read_reg: {hex(dd)}')
    #
    #
    #
    #
    #
    #
    #
    # delta_res = 0.565
    #
    # uart_close()