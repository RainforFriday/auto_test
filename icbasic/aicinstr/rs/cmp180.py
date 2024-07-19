# encoding: utf-8

# readme:  traces
# WLAN measurements>Command reference>Measurement result commands>Modulation single vaules,OFDM>CALCulate:WLAN:MEAS<i>:MEValuation:MODulation:CURRent?

import os
import sys


from aicinstr.rs.genericinstrument import *

__version__ = "v0.1"


class CMP180(GenericInstrument):
    def __init__(self, MeasNum = 2):
        super(GenericInstrument, self).__init__()
        self.tx_connector = ["RF1.1", "RF2.1", "RF1.2", "RF2.2"]
        self.MeasNum = MeasNum

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
        self.write("ROUTe:GPRF:MEAS{}:SCENario:SALone {} RX1".format(self.MeasNum, route))
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:SPAN FSWeep".format(self.MeasNum))
        return True

    def spa_cfreq(self, freq=2400):  # cfreq Mhz
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:CENTer {}".format(self.MeasNum, freq*1.0e6))
        return True

    def spa_span(self, span=40):  # span MHz
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:SPAN {}".format(self.MeasNum, span*1.0e6))
        return True

    def spa_start(self, f_start=2300):
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:STARt {}".format(self.MeasNum, f_start*1.0e6))
        return True

    def spa_stop(self, f_stop=2500):
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:STARt {}".format(self.MeasNum, f_stop*1.0e6))
        return True

    def spa_reflvl(self, pwr=20.0):  # dBm
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:ENPower {}".format(self.MeasNum, pwr))
        return True

    def spa_rbw(self, rbw=1.0):  # MHz
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:RBW {}".format(self.MeasNum, rbw*1.0e6))
        return True

    def spa_rbw_auto(self):
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:RBW:AUTO ON".format(self.MeasNum))
        return True

    def spa_vbw(self, vbw=1.0):  # MHz
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:VBW {}".format(self.MeasNum, vbw*1.0e6))
        return True

    def spa_vbw_auto(self):
        self.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:VBW:AUTO ON".format(self.MeasNum))
        return True

    def spa_on(self):
        self.write("INITiate:GPRF:MEAS{}:POWer".format(self.MeasNum))

    def spa_off(self):
        self.write("STOP:GPRF:MEAS{}:POWer".format(self.MeasNum))

    def spa_peak_pwr(self):
        return self.query("FETCh:GPRF:MEAS{}:SPECtrum:MAXimum:CURRent?".format(self.MeasNum)).split(",")[1:]

    ####3 fft mode
    def fsp_peak(self):
        return self.query("FETCh:GPRF:MEAS{}:FFTSanalyzer:PEAKs:AVERage?".format(self.MeasNum)).split(",")[1:3]

    def fsp_peak_pwr(self):
        try:
            return float(self.fsp_peak()[1])
        except:
            return 0

    def fsp_peak_freq(self):
        try:
            return float(self.fsp_peak()[0])
        except:
            return 0

    def fsp_span(self, span=1.25):
        if span not in [1.25, 2.5, 5, 10, 20, 40, 80, 160]:
            print("SPAN SET ERROR")
            sys.exit(0)
        else:
            self.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:FSPan {}".format(self.MeasNum, span*1.0e6))
            return True

    def fsp_get_cfreq(self):
        return self.query("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency?".format(self.MeasNum))

    def fsp_set_cfreq(self, freq=2400):  # cfreq Mhz
        self.write("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq*1.0e6))
        return True

    def fsp_set_cfreq_by_ch(self, ch=1):
        # defalut unit : Hz
        if int(ch) < 15:
            freq = (2407 + 5*int(ch))*1E6
        elif (int(ch) > 30) and (int(ch) < 170) :
            freq = (5000 + 5*int(ch))*1E6
        else:
            freq = int(ch)*1E6
        self.write("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))

    def fsp_on(self):
        self.write("INITiate:GPRF:MEAS{}:FFTSanalyzer".format(self.MeasNum))

    def fsp_off(self):
        self.write("ABORt:GPRF:MEAS{}:FFTSanalyzer".format(self.MeasNum))

    def fsp_set_enpwr(self, power=20):
        self.write("CONFigure:GPRF:MEAS{}:RFSettings:ENPower {}".format(self.MeasNum, power))

    def fsp_auto_enpwr(self):
        self.fsp_set_enpwr(30)
        self.fsp_on()
        peak_pwr = self.fsp_peak_pwr()
        self.fsp_set_enpwr(int(float(peak_pwr)) + 3)
        # self.fsp_off()
        return True

    def fsp_cw_mode(self):
        self.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:REPetion CONTinuous:".format(self.MeasNum))

    def fsq_len_set(self):
        self.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:FFTLength 2048".format(self.MeasNum))

    def fsq_mode(self, route="RF1C"):
        self.write("ROUTe:GPRF:MEAS{}:RFSettings:CONNector {}".format(self.MeasNum, route))
        return True

    # WLAN Signal Measure Section
    def wlan_set_route(self, route="RF1.1"):  # Update cmp180
        self.write("ROUTe:WLAN:MEAS{}:SPATh \"{}\"".format(self.MeasNum, route))
        return True

    def wlan_set_attenuation(self, att=0):  # Update cmp180
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:EATTenuation1 {}".format(self.MeasNum, att))
        return True

    def wlan_set_band(self, band="B24Ghz"):  # Update cmp180
        # 2.4G band: B24GHz
        # 4G band: B4GHz
        # 5G band: B5GHz
        # 6G band: B6GHz
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency:BAND {}".format(self.MeasNum, band))
        return True

    def wlan_set_peakpwr(self, peakpower=30): # update cmp180
        # the expected nominal power
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:ENPower1 {}".format(self.MeasNum, peakpower))
        return True

    def wlan_set_bandwidth(self, BW="40"):
        # BW05mhz, BW10mhz, BW20mhz, BW40mhz, BW80mhz, BW16mhz:160M, BW32mhz: 320M
        if BW in ["20", "20M", "20m", "20MHz", "20mhz"]:
            bandwidth = "BW20mhz"
        elif BW in ["40", "40M", "40m", "40MHz", "40mhz"]:
            bandwidth = "BW40mhz"
        elif BW in ["80", "80M", "80m", "80MHz", "80mhz"]:
            bandwidth = "BW80mhz"
        else:
            print("BindWidth set error: {}".format(BW))
            sys.exit(0)
        self.write("CONFigure:WLAN:MEAS{}:ISIGnal:BWIDth {}".format(self.MeasNum, bandwidth))
        return True

    def wlan_set_freq(self, freq=2.412E9):  # cmp180 update
        # defalut unit : Hz
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
        return True

    def wlan_set_channel(self, ch=1):
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency:CHANnels {}".format(self.MeasNum, ch))
        return True

    def wlan_set_freq_by_ch(self, ch=1):
        # defalut unit : Hz
        if int(ch) < 15:
            freq = (2407 + 5*int(ch))*1E6
        elif (int(ch) > 30) and (int(ch) < 170) :
            freq = (5000 + 5*int(ch))*1E6
        else:
            freq = int(ch)*1E6
        self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))

    def wlan_set_standard(self, standard: object = "11n") -> object:
        # standard dict
        STANDARD = {"11n": "HTOFdm", "11b": "DSSS", "11g": "LOFDm", "11ac": "VHTofdm", "11ax": "HEOFdm", "11be": "EHTOFdm"}
        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11b/11g".format(standard))
            sys.exit(0)
        self.write("CONFigure:WLAN:MEAS{}:ISIGnal:STANdard {}".format(self.MeasNum, STANDARD[standard]))
        return True

    def wlan_set_bursttype(self, btype="MIX"):
        # burst type: MIXed | GREenfield | DLIN | AUTO
        # MIXed (802.11n): compatibility mode supporting coexistence of 802.11a/b/g and n networks
        # GREenfield (802.11n): greenfield mode where only standard 802.11n is used
        # DLIN (802.11a/g OFDM): direct link
        # AUTO (802.11b/g DSSS): automatic detection
        self.write("CONFigure:WLAN:MEAS{}:ISIGnal:BTYPe {}".format(self.MeasNum, btype))
        return True

    def wlan_meas_start(self):
        self.write("INITiate:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        self.write("CONFigure:WLAN:MEAS{}:MEValuation:SCOunt:MODulation 10".format(self.MeasNum))
        return True

    def wlan_meas_stop(self):
        self.write("STOP:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        return True

    def wlan_meas_abort(self):
        self.write("ABORt:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        return True

    def wlan_meas_getresults(self):
        pass

    def wlan_meas_11b_avg(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:MODulation:DSSS:AVERage?".format(self.MeasNum))

    def wlan_meas_11b_evm(self):
        return self.wlan_meas_11b_avg().split(",")[5]

    def wlan_meas_11b_pwr(self):
        return self.wlan_meas_11b_avg().split(",")[4]

    def wlan_meas_avg(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:MODulation:AVERage?".format(self.MeasNum))

    def wlan_meas_pwr(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[12]))
        except:
            return "-100"

    def wlan_meas_peak_pwr(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[13]))
        except:
            return "-100"

    def wlan_meas_evm(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[15]))
        except:
            return "0"

    def wlan_meas_freq_error(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[18]))

    def wlan_meas_clock_error(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[19]))

    def wlan_meas_IQoffset(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[20]))

    def wlan_meas_DCPwr(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[21]))

    def wlan_meas_gain_imb(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[22]))

    def wlan_meas_quad_error(self):
        return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[23]))

    def wlan_auto_peak_pwr(self):
        self.wlan_set_peakpwr(30)
        self.wlan_meas_start()
        time.sleep(2)
        peak_pwr = self.wlan_meas_peak_pwr()
        self.wlan_set_peakpwr(int(float(peak_pwr)) + 3)
        self.wlan_meas_abort()
        return True

    def wlan_meas_tsmask_avg(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:AVERage?".format(self.MeasNum))

    def wlan_meas_tsmask_min(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:MINimum?".format(self.MeasNum))

    def wlan_meas_tsmask_max(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:MAXimum?".format(self.MeasNum))

    def wlan_meas_tsmask_current(self):
        return self.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:CURRent?".format(self.MeasNum))




if __name__ == "__main__":
    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)
    print(CMPX.id_string())
    print(CMPX.wlan_meas_evm())
    # evm = CMPX.wlan_meas_evm()
    # print(evm)
    print(CMPX.wlan_meas_pwr())

    CMPX.close()
