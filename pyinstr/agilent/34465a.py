import os
import sys


from pyinstr.rs.genericinstrument import *

class CMW(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()
        self.tx_connector = ["RF1C", "RF1O", "RF2C"]

    def reset(self):
        self.write("*RST; *OPC?")

    def clear(self):
        self.write("*CLS; *OPC?")

    #  RF Signal Generate Section
    def sge_cw_mode(self, route="RF1O"):
        if route not in self.tx_connector:
            print("Set TXConnector Error, Abort!!!")
            sys.exit(0)
        self.write("ROUTe:GPRF:GEN:SCENario:SALone {}, TX1".format(route))
        self.write("SOURce:GPRF:GEN:BBMode CW")
        return True

    def sge_arb_mode(self, route="RF1C"):
        if route not in self.tx_connector:
            print("Set TXConnector Error, Abort!!!")
            sys.exit(0)
        self.write("ROUTe:GPRF:GEN:SCENario:SALone {}, TX1".format(route))
        self.write("SOURce:GPRF:GEN:BBMode ARB")
        return True

    def arb_file(self, standard="11n"):
        # standard dict
        STANDARD = {"11n": "\"D:\\aic_wave\\aic_wave_ydy\\11n_40m_64qam.wv\"", "11ac": "\"D:\\aic_wave\\aic_wave_ydy\\11ac_40m_256qam.wv\"", "11ax": "\"D:\\aic_wave\\aic_wave_ydy\\11ax_40m_1024qam.wv\""}
        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11ac/11ax".format(standard))
            sys.exit(0)
        self.write("SOURce:GPRF:GEN:ARB:FILE {}".format(STANDARD[standard]))
        return True

    def sge_cw_set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.write("SOURce:GPRF:GEN:RFSettings:FREQuency {}".format(cfreq*1.0e6))
        return True

    def sge_cw_set_power(self, pwr):  # pwr unit dbm
        self.write("SOURce:GPRF:GEN:RFSettings:LEVel {}".format(pwr))
        return True

    def sge_cw_pwr_on(self):
        self.write("SOURce:GPRF:GEN:STATe ON")
        return self.write("*OPC?")
        # return True

    def sge_cw_pwr_off(self):
        self.write("SOURce:GPRF:GEN:STATe OFF")
        return True

    # RF Signal Measure Section
    def spa_mode(self, route="RF1C"):
        self.write("ROUTe:GPRF:MEAS1:SCENario:SALone {} RX1".format(route))
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FREQuency:SPAN FSWeep")
        return True

    def spa_cfreq(self, freq=2400):  # cfreq Mhz
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FREQuency:CENTer {}".format(freq*1.0e6))
        return True

    def spa_span(self, span=40):  # span MHz
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FREQuency:SPAN {}".format(span*1.0e6))
        return True

    def spa_start(self, f_start=2300):
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FREQuency:STARt {}".format(f_start*1.0e6))
        return True

    def spa_stop(self, f_stop=2500):
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FREQuency:STARt {}".format(f_stop*1.0e6))
        return True

    def spa_reflvl(self, pwr=20.0):  # dBm
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:ENPower {}".format(pwr))
        return True

    def spa_rbw(self, rbw=1.0):  # MHz
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FSWeep:RBW {}".format(rbw*1.0e6))
        return True

    def spa_rbw_auto(self):
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FSWeep:RBW:AUTO ON")
        return True

    def spa_vbw(self, vbw=1.0):  # MHz
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FSWeep:VBW {}".format(vbw*1.0e6))
        return True

    def spa_vbw_auto(self):
        self.write("CONFigure:GPRF:MEAS1:SPECtrum:FSWeep:VBW:AUTO ON")
        return True

    def spa_on(self):
        self.write("INITiate:GPRF:MEAS1:POWer")

    def spa_off(self):
        self.write("STOP:GPRF:MEAS1:POWer")

    def spa_peak_pwr(self):
        aaa = self.query("FETCh:GPRF:MEAS1:SPECtrum:MAXimum:CURRent?").split(",")[1:]
        return aaa

    ####3 fft mode
    def fsp_peak(self):
        return self.query("FETCh:GPRF:MEAS1:FFTSanalyzer:PEAKs:CURRent?").split(",")[1:3]

    def fsp_span(self, span=1.25):
        if span not in [1.25,2.5,5,10,20,40,80,160]:
            print("SPAN SET ERROR")
            sys.exit(0)
        else:
            self.write("CONFigure:GPRF:MEAS1:FFTSanalyzer:FSPan {}".format(span*1.0e6))
            return True

    def fsp_get_cfreq(self):
        return self.query("CONFigure:GPRF:MEAS1:RFSettings:FREQuency?")

    def fsp_cfreq(self, freq=2400):  # cfreq Mhz
        self.write("CONFigure:GPRF:MEAS1:RFSettings:FREQuency {}".format(freq*1.0e6))
        return True

    def fsp_on(self):
        self.write("INITiate:GPRF:MEAS1:FFTSanalyzer")

    def fsp_off(self):
        self.write("ABORt:GPRF:MEAS1:FFTSanalyzer")

    def fsp_pwr(self,power=20):
        self.write("CONFigure:GPRF:MEAS1:RFSettings:ENPower {}".format(power))

    def fsp_cw_mode(self):
        self.write("CONFigure:GPRF:MEAS1:FFTSanalyzer:REPetion CONTinuous:")

    def fsq_len_set(self):
        self.write("CONFigure:GPRF:MEAS1:FFTSanalyzer:FFTLength 2048")

    def fsq_mode(self, route="RF1C"):
        self.write("ROUTe:GPRF:MEAS:RFSettings:CONNector {}".format(route))
        return True
    # WLAN Signal Measure Section
    def wlan_set_route(self, route="RX1"):
        self.write("ROUTe:WLAN:MEAS1:SCENario:SALone RF1C, RX1")
        return True

    def wlan_set_attenuation(self, att=0):
        self.write("CONFigure:WLAN:MEAS1:RFSettings:EATTenuation {}".format(att))
        return True

    def wlan_set_band(self, band="B24GHz"):
        # 2.4G band: B24GHz
        # 5G band: B5GHz
        self.write("CONFigure:WLAN:MEAS1:RFSettings:FREQuency:BAND {}".format(band))
        return True

    def wlan_set_peakpwr(self, peakpower=30):
        # the expected nominal power
        self.write("CONFigure:WLAN:MEAS1:RFSettings:ENPower {}".format(peakpower))
        return True

    def wlan_set_bandwidth(self, bandwidth="BW40"):
        self.write("CONFigure:WLAN:MEAS1:ISIGnal:BWIDth {}".format(bandwidth))
        return True

    def wlan_set_freq(self, freq=2.412E9):
        # defalut unit : Hz
        self.write("CONFigure:WLAN:MEAS1:RFSettings:FREQuency {}".format(freq))
        return True

    def wlan_set_channel(self, ch=1):
        self.write("CONFigure:WLAN:MEAS1:RFSettings:FREQuency:SCHannel {}".format(ch))
        return True

    def wlan_set_standard(self, standard: object = "11n") -> object:
        # standard dict
        STANDARD = {"11n": "NSISo", "11b": "BDSSs", "11g": "GOFDm", "11ac": "ACSIso","11ax": "HEOFdm"}
        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11b/11g".format(standard))
            sys.exit(0)
        self.write("CONFigure:WLAN:MEAS1:ISIGnal:STANdard {}".format(STANDARD[standard]))
        return True

    def wlan_set_bursttype(self, btype="MIX"):
        # burst type: MIXed | GREenfield | DLIN | AUTO
        # MIXed (802.11n): compatibility mode supporting coexistence of 802.11a/b/g and n networks
        # GREenfield (802.11n): greenfield mode where only standard 802.11n is used
        # DLIN (802.11a/g OFDM): direct link
        # AUTO (802.11b/g DSSS): automatic detection
        self.write("CONFigure:WLAN:MEAS1:ISIGnal:BTYPe {}".format(btype))
        return True

    def wlan_meas_start(self):
        self.write("INITiate:WLAN:MEAS1:MEValuation")
        self.write("CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 100")
        return True

    def wlan_meas_stop(self):
        self.write("STOP:WLAN:MEAS1:MEValuation")
        return True

    def wlan_meas_abort(self):
        self.write("ABORt:WLAN:MEAS1:MEValuation")
        return True

    def wlan_meas_getresults(self):
        self.write()

    def wlan_meas_avg(self):
        return self.query("FETCh:WLAN:MEAS1:MEValuation:MODulation:AVERage?")

    def wlan_meas_11b_avg(self):
        return self.query("FETCh:WLAN:MEAS1:MEValuation:MODulation:DSSS:AVERage?")

    def wlan_meas_11b_evm(self):
        return self.wlan_meas_11b_avg().split(",")[5]

    def wlan_meas_11b_pwr(self):
        return self.wlan_meas_11b_avg().split(",")[4]

    def wlan_meas_evm(self):
        return self.wlan_meas_avg().split(",")[15]

    def wlan_meas_pwr(self):
        return self.wlan_meas_avg().split(",")[12]

    def wlan_meas_DCPwr(self):
        return self.wlan_meas_avg().split(",")[21]

    def wlan_meas_IQoffset(self):
        return self.wlan_meas_avg().split(",")[20]

    def wlan_meas_clock_error(self):
        return self.wlan_meas_avg().split(",")[19]

    def wlan_meas_gain_imb(self):
        return self.wlan_meas_avg().split(",")[22]

    def wlan_meas_quar_error(self):
        return self.wlan_meas_avg().split(",")[23]

if __name__ == "__main__":
    host = "10.21.10.190"
    port = 5025
    CMW1 = CMW()
    CMW1.open_tcp(host, port)
    print(CMW1.id_string())
    CMW1.wlan_set_route()
    CMW1.wlan_set_freq(5180e+6)
    CMW1.wlan_set_peakpwr(-10)
    CMW1.wlan_set_standard("11n")

    CMW1.wlan_set_bandwidth("BW40")

    CMW1.wlan_meas_start()
    time.sleep(6)
    CMW1.wlan_meas_stop()
    a=CMW1.wlan_meas_avg()
    #print(a)
    evm_11b=CMW1.wlan_meas_11b_evm()
    pwr_11b = CMW1.wlan_meas_11b_pwr()
    evm = CMW1.wlan_meas_evm()
    pwr = CMW1.wlan_meas_pwr()

    iq = CMW1.wlan_meas_IQoffset()
    dc = CMW1.wlan_meas_DCPwr()
    freq_error = CMW1.wlan_meas_clock_error()
    gain_imb=CMW1.wlan_meas_gain_imb()
    quar_error=CMW1.wlan_meas_quar_error()
    print(dc)
    print(gain_imb)
    print(quar_error)
    print(freq_error)
    print(CMW1.wlan_meas_avg())
    print(evm_11b)
    print(pwr_11b)
    print(evm)
    print(pwr)
    print(iq)

    CMW1.close()