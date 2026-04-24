# encoding: utf-8

# readme:  traces
# WLAN measurements>Command reference>Measurement result commands>Modulation single vaules,OFDM>CALCulate:WLAN:MEAS<i>:MEValuation:MODulation:CURRent?

import os
import socket
import sys
import time
import sys
import pyvisa
sys.path.append(r"D:\8819\8819_python\scripts\aic_repos")

from icbasic.aicinstr.rs.genericinstrument import *

__version__ = "v0.1"


class CMP180vs():
    def __init__(self, address, MeasNum = 1):
        # super(GenericInstrument, self).__init__()
        self.tx_connector = ["RF1.8", "RF2.1", "RF1.2", "RF2.2"]
        self.MeasNum = MeasNum
        self.sa = self.connect_cmp(address)

    def __del__(self):
        self.sa.close()

    def close(self):
        self.sa.close()

    def connect_cmp(self, address):
        # 创建资源管理器
        rm = pyvisa.ResourceManager()

        # 设备地址（根据实际情况修改）
        # device_address = "TCPIP0::10.21.10.166::hislip0::INSTR"

        try:
            # 建立连接
            sa = rm.open_resource(address)
            sa.timeout = 5000  # 设置超时时间(ms)

            # 验证连接
            idn = sa.query("*IDN?")
            print(f"successful : {idn.strip()}")

            return sa

        except pyvisa.errors.VisaIOError as e:
            print(f"fail : {str(e)}")
            return None

    def reset(self):
        self.sa.write("*RST; *OPC?")

    def clear(self):
        self.sa.write("*CLS; *OPC?")

    # GPRF ARB

    def sge_arb_on(self):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:STATe ON')

    def sge_arb_off(self):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:STATe OFF')

    def sge_arb_rep(self, mode="SINGle"):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:REPetition {mode}')

    def sge_arb_rep_count(self):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:NREPetition 1000')

    def sge_arb_set_cfreq(self, freq):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:FREQuency 0, {freq}E+6')

    def sge_arb_set_lvl(self, lvl):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:LRMS 0, {lvl}')

    def sge_arb_list_incre(self, mode= "ACYCles"):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:LINCrement 0, {mode}')

    def sge_arb_set_wave(self, wave):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:APOol:FILE "/home/instrument/fw/data/waveform/RS_wifi_waveform/{wave}"')
        ## self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:SIGNal 0, "@WAVEFORM/RS_wifi_waveform/{wave}"')
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:SIGNal 0, "{wave}"')

    def sge_set_route(self, route="RF1.8"):
        self.sa.write(f'SOURce:GPRF:GEN:SEQuencer:RFSettings:SPATh:CSET GLOBal')
        versions = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"]

        for i, version in enumerate(versions):
            if version in route:
                config_list = ["OFF"] * 8
                config_list[i] = "ON"
                config_str = ", ".join(config_list)
                self.sa.write(f'CONFigure:GPRF:GEN:SPATh:USAGe {config_str}')
                return

        # 默认配置
        print(f"未匹配到路由: {route}")
        self.sa.write(f'CONFigure:GPRF:GEN:SPATh:USAGe OFF, OFF, OFF, OFF, OFF, OFF, OFF, ON')


        # if "1.8" in route:
        #     self.sa.write(f'CONFigure:GPRF:GEN:SPATh:USAGe OFF, OFF, OFF, OFF, OFF, OFF, OFF, ON')
        # elif "1.1" in route:
        #     self.sa.write(f'CONFigure:GPRF:GEN:SPATh:USAGe ON, OFF, OFF, OFF, OFF, OFF, OFF, OFF')
        # else:
        #     self.sa.write(f'CONFigure:GPRF:GEN:SPATh:USAGe ON, OFF, OFF, OFF, OFF, OFF, OFF, ON')





    #  RF Signal Generate Section
    def sge_cw_mode(self, route="RF1O"):
        if route not in self.tx_connector:
            print("Set TXConnector Error, Abort!!!")
            sys.exit(0)
        self.sa.write("ROUTe:GPRF:GEN:SCENario:SALone {}, TX1".format(route))
        self.sa.write("SOURce:GPRF:GEN:BBMode CW")
        return True

    def sge_arb_mode(self, route="RF1.8"):
        if route not in self.tx_connector:
            print("Set TXConnector Error, Abort!!!")
            sys.exit(0)
        self.sa.write("ROUTe:GPRF:GEN:SCENario:SALone {}, TX1".format(route))
        self.sa.write("SOURce:GPRF:GEN:BBMode ARB")
        return True

    def arb_file(self, standard="11n"):
        # standard dict
        STANDARD = {"11n": "\"D:\\aic_wave\\aic_wave_ydy\\11n_40m_64qam.wv\"", "11ac": "\"D:\\aic_wave\\aic_wave_ydy\\11ac_40m_256qam.wv\"", "11ax": "\"D:\\aic_wave\\aic_wave_ydy\\11ax_40m_1024qam.wv\""}
        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11ac/11ax".format(standard))
            sys.exit(0)
        self.sa.write("SOURce:GPRF:GEN:ARB:FILE {}".format(STANDARD[standard]))
        return True

    def sge_cw_set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.sa.write("SOURce:GPRF:GEN:RFSettings:FREQuency {}".format(cfreq*1.0e6))
        return True

    def sge_cw_set_power(self, pwr):  # pwr unit dbm
        self.sa.write("SOURce:GPRF:GEN:RFSettings:LEVel {}".format(pwr))
        return True

    def sge_cw_pwr_on(self):
        self.sa.write("SOURce:GPRF:GEN:STATe ON")
        return self.sa.write("*OPC?")
        # return True

    def sge_cw_pwr_off(self):
        self.sa.write("SOURce:GPRF:GEN:STATe OFF")
        return True

    # RF Signal Measure Section
    def spa_mode(self, route="RF1C"):
        self.sa.write("ROUTe:GPRF:MEAS{}:SCENario:SALone {} RX1".format(self.MeasNum, route))
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:SPAN FSWeep".format(self.MeasNum))
        return True

    def spa_cfreq(self, freq=2400):  # cfreq Mhz
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:CENTer {}".format(self.MeasNum, freq*1.0e6))
        return True

    def spa_span(self, span=40):  # span MHz
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:SPAN {}".format(self.MeasNum, span*1.0e6))
        return True

    def spa_start(self, f_start=2300):
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:STARt {}".format(self.MeasNum, f_start*1.0e6))
        return True

    def spa_stop(self, f_stop=2500):
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FREQuency:STARt {}".format(self.MeasNum, f_stop*1.0e6))
        return True

    def spa_reflvl(self, pwr=20.0):  # dBm
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:ENPower {}".format(self.MeasNum, pwr))
        return True

    def spa_rbw(self, rbw=1.0):  # MHz
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:RBW {}".format(self.MeasNum, rbw*1.0e6))
        return True

    def spa_rbw_auto(self):
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:RBW:AUTO ON".format(self.MeasNum))
        return True

    def spa_vbw(self, vbw=1.0):  # MHz
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:VBW {}".format(self.MeasNum, vbw*1.0e6))
        return True

    def spa_vbw_auto(self):
        self.sa.write("CONFigure:GPRF:MEAS{}:SPECtrum:FSWeep:VBW:AUTO ON".format(self.MeasNum))
        return True

    def spa_on(self):
        self.sa.write("INITiate:GPRF:MEAS{}:POWer".format(self.MeasNum))

    def spa_off(self):
        self.sa.write("STOP:GPRF:MEAS{}:POWer".format(self.MeasNum))

    def spa_peak_pwr(self):
        return self.sa.query("FETCh:GPRF:MEAS{}:SPECtrum:MAXimum:CURRent?".format(self.MeasNum)).split(",")[1:]

    ####3 fft mode
    def fsp_peak(self):
        return self.sa.query("FETCh:GPRF:MEAS{}:FFTSanalyzer:PEAKs:AVERage?".format(self.MeasNum)).split(",")[1:3]

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
            self.sa.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:FSPan {}".format(self.MeasNum, span*1.0e6))
            return True

    def fsp_get_cfreq(self):
        return self.sa.query("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency?".format(self.MeasNum))

    def fsp_set_cfreq(self, freq=2400):  # cfreq Mhz
        self.sa.write("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq*1.0e6))
        return True

    def fsp_set_cfreq_by_ch(self, ch=1):
        # defalut unit : Hz
        if int(ch) < 15:
            freq = (2407 + 5*int(ch))*1E6
        elif (int(ch) > 30) and (int(ch) < 170) :
            freq = (5000 + 5*int(ch))*1E6
        else:
            freq = int(ch)*1E6
        self.sa.write("CONFigure:GPRF:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))

    def fsp_on(self):
        self.sa.write("INITiate:GPRF:MEAS{}:FFTSanalyzer".format(self.MeasNum))

    def fsp_off(self):
        self.sa.write("ABORt:GPRF:MEAS{}:FFTSanalyzer".format(self.MeasNum))

    def fsp_set_enpwr(self, power=20):
        self.sa.write("CONFigure:GPRF:MEAS{}:RFSettings:ENPower {}".format(self.MeasNum, power))

    def fsp_auto_enpwr(self):
        self.fsp_set_enpwr(30)
        self.fsp_on()
        peak_pwr = self.fsp_peak_pwr()
        self.fsp_set_enpwr(int(float(peak_pwr)) + 5)
        # self.fsp_off()
        return True

    def fsp_cw_mode(self):
        self.sa.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:REPetion CONTinuous:".format(self.MeasNum))

    def fsq_len_set(self):
        self.sa.write("CONFigure:GPRF:MEAS{}:FFTSanalyzer:FFTLength 2048".format(self.MeasNum))

    def fsq_mode(self, route="RF1C"):
        self.sa.write("ROUTe:GPRF:MEAS{}:RFSettings:CONNector {}".format(self.MeasNum, route))
        return True

    def fsq_set_route(self, route="RF1.1"):  # Update cmp180
        cmpx_route_list = []
        for xnum in range(1, 9):
            for ynum in range(1, 3):
                cmpx_route_list.append("RF{}.{}".format(ynum, xnum))
        if route in cmpx_route_list:
            self.sa.write("ROUTe:GPRF:MEAS{}:SPATh \"{}\"".format(self.MeasNum, route))
            return True
        else:
            print("Route ERROR: {}".format(route))

    # WLAN Signal Measure Section
    def wlan_set_route(self, route="RF1.1"):  # Update cmp180
        self.sa.write("ROUTe:WLAN:MEAS{}:SPATh \"{}\"".format(self.MeasNum, route))
        return True

    def wlan_set_attenuation(self, att=0):  # Update cmp180
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:EATTenuation1 {}".format(self.MeasNum, att))
        return True

    def wlan_set_band(self, band="B24Ghz"):  # Update cmp180
        # 2.4G band: B24GHz
        # 4G band: B4GHz
        # 5G band: B5GHz
        # 6G band: B6GHz
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency:BAND {}".format(self.MeasNum, band))
        return True

    def wlan_set_peakpwr(self, peakpower=30): # update cmp180
        # the expected nominal power
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:ENPower1 {}".format(self.MeasNum, peakpower))
        return True

    def wlan_set_wlan_Adjust_lvl(self, lvlRangInterval=0.01): # update cmp180
        # CONFigure:WLAN:MEAS<i>:RFSettings:LRINterval <LvlRangInterval>
        # self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:LRINterval {}".format(self.MeasNum, lvlRangInterval))
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:LRSTart".format(self.MeasNum))
        time.sleep(0.2)
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
        self.sa.write("CONFigure:WLAN:MEAS{}:ISIGnal:BWIDth {}".format(self.MeasNum, bandwidth))
        return True

    def wlan_set_freq(self, freq=2.412E9):  # cmp180 update
        # defalut unit : Hz
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
        return True

    def wlan_set_channel(self, ch=1):
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency:CHANnels {}".format(self.MeasNum, ch))
        return True

    def wlan_set_freq_by_ch(self, ch=1):
        # defalut unit : Hz
        if int(ch) < 15:
            freq = (2407 + 5*int(ch))*1E6
        elif (int(ch) > 30) and (int(ch) < 170) :
            freq = (5000 + 5*int(ch))*1E6
        else:
            freq = int(ch)*1E6
        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))

    def wlan_set_freq_by_ch_6e(self, ch=1):
        # defalut unit : Hz

        freq = (5955 + 5 * (int(ch)-1)) * 1E6

        self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))

    def wlan_set_standard(self, standard: object = "11n") -> object:
        # standard dict
        STANDARD = {"11n": "HTOFdm", "11b": "DSSS", "11g": "LOFDm", "11ac": "VHTofdm", "11ax": "HEOFdm", "11be": "EHTOFdm"}
        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11b/11g".format(standard))
            sys.exit(0)
        self.sa.write("CONFigure:WLAN:MEAS{}:ISIGnal:STANdard {}".format(self.MeasNum, STANDARD[standard]))
        return True

    def wlan_set_bursttype(self, btype="MIX"):
        # burst type: MIXed | GREenfield | DLIN | AUTO
        # MIXed (802.11n): compatibility mode supporting coexistence of 802.11a/b/g and n networks
        # GREenfield (802.11n): greenfield mode where only standard 802.11n is used
        # DLIN (802.11a/g OFDM): direct link
        # AUTO (802.11b/g DSSS): automatic detection
        self.sa.write("CONFigure:WLAN:MEAS{}:ISIGnal:BTYPe {}".format(self.MeasNum, btype))
        return True

    def wlan_meas_start(self):
        self.sa.write("INITiate:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        self.sa.write("CONFigure:WLAN:MEAS{}:MEValuation:SCOunt:MODulation 30".format(self.MeasNum))
        return True

    def wlan_meas_stop(self):
        self.sa.write("STOP:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        return True

    def wlan_meas_abort(self):
        self.sa.write("ABORt:WLAN:MEAS{}:MEValuation".format(self.MeasNum))
        return True

    def wlan_meas_getresults(self):
        pass

    def wlan_meas_11b_avg(self):
        return self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:MODulation:DSSS:AVERage?".format(self.MeasNum))

    def wlan_meas_11b_evm_peak(self):
        try:
            evm_peak11b = "{:.2f}".format(float(self.wlan_meas_11b_avg().split(",")[5]))
        except ValueError:
            evm_peak11b = '-100'
        return evm_peak11b

    def wlan_meas_11b_evm_rms(self):
        try:
            evm11b = "{:.2f}".format(float(self.wlan_meas_11b_avg().split(",")[6]))
        except ValueError:
            evm11b = '-100'
        return evm11b

    def wlan_meas_11b_pwr(self):
        try:
            pwr11b = "{:.2f}".format(float(self.wlan_meas_11b_avg().split(",")[4]))
        except ValueError:
            pwr11b = '-100'
        return pwr11b

    # def wlan_meas_avg(self):
    #     for _ in range(2):
    #         str = self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:MODulation:AVERage?".format(self.MeasNum))
    #         time.sleep(0.5)
    #     return str

    def wlan_meas_avg(self):
        return self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:MODulation:AVERage?".format(self.MeasNum))

    def wlan_meas_pwr(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[12]))
        except:
            return "-100"

    def wlan_meas_peak_pwr(self):
        try:
            # print(self.wlan_meas_avg().split(",")[13])
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[13]))
        except:
            return "-100"

    def wlan_meas_evm(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[15]))
        except:
            return "-100"

    def wlan_meas_evm_peak(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[14]))
        except:
            return "-100"

    def wlan_meas_freq_error(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[18]))
        except:
            return "-100"

    def wlan_meas_11b_clock_error(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_11b_avg().split(",")[8]))
        except:
            return "-100"

    def wlan_meas_clock_error(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[19]))
        except:
            return "-100"

    def wlan_meas_IQoffset(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[20]))
        except:
            return "-100"

    def wlan_meas_DCPwr(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[21]))
        except:
            return "-100"

    def wlan_meas_gain_imb(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[22]))
        except:
            return "-100"

    def wlan_meas_quad_error(self):
        try:
            return "{:.2f}".format(float(self.wlan_meas_avg().split(",")[23]))
        except:
            return "-100"

    def wlan_auto_peak_pwr(self):
        self.wlan_set_peakpwr(35)
        self.wlan_meas_start()
        time.sleep(2)
        peak_pwr = self.wlan_meas_peak_pwr()
        # if peak_pwr == "-100":
        #     self.wlan_set_peakpwr(10)
        #     self.wlan_meas_start()
        #     time.sleep(2)
        #     peak_pwr = self.wlan_meas_peak_pwr()
        if peak_pwr == "-100":
            # self.wlan_set_peakpwr(40)
            self.wlan_set_wlan_Adjust_lvl()
            self.wlan_meas_start()
            time.sleep(2)
            peak_pwr = self.wlan_meas_peak_pwr()
        self.wlan_set_peakpwr(int(float(peak_pwr)) + 3)
        self.wlan_meas_abort()
        return True

    def wlan_Adjust_lvl(self):
        # self.wlan_set_peakpwr(40)
        self.wlan_set_wlan_Adjust_lvl()
        # time.sleep(0.2)


    def wlan_meas_tsmask_avg(self):
        # time.sleep(2)
        # self.sa.write("INIT:IMM;*OPC?")
        self.sa.write("*OPC?")
        try:
            # self.sa.read().strip()
            time.sleep(0.3)
            meas_pwr = self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:AVERage?".format(self.MeasNum))

            # for _ in range(2):
            #     meas_pwr = self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:AVERage?".format(self.MeasNum))
            #     time.sleep(0.3)


            # print(f'measure_pwr {meas_pwr}')
            # meas_pwr = '-100'
            # if ready == '1':
            #     meas_pwr=self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:AVERage?".format(self.MeasNum))
            #     time.sleep(0.2)
            # else:
            #     meas_pwr='time_out'
        except Exception as e:
            meas_pwr = 'time_out'
        # print(f'measure_pwr {meas_pwr}')
        return meas_pwr

    def wlan_meas_tsmask_avg_maxval(self):
        return self.__get_mask_margin__(self.wlan_meas_tsmask_avg())

    def wlan_meas_tsmask_min(self):
        return self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:MINimum?".format(self.MeasNum))

    def wlan_meas_tsmask_min_maxval(self):
        return self.__get_mask_margin__(self.wlan_meas_tsmask_min())

    def wlan_meas_tsmask_max(self):
        return self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:MAXimum?".format(self.MeasNum))

    def wlan_meas_tsmask_max_maxval(self):
        return self.__get_mask_margin__(self.wlan_meas_tsmask_max())

    def wlan_meas_tsmask_current(self):
        return self.sa.query("FETCh:WLAN:MEAS{}:MEValuation:TSMask:CURRent?".format(self.MeasNum))

    def wlan_meas_tsmask_current_maxval(self):
        return self.__get_mask_margin__(self.wlan_meas_tsmask_current())

    def __get_mask_margin__(self, mask_str):
        mask_margin_lines = mask_str.split(",")[2:]
        # print(mask_margin_lines)
        try:
            mask_margin_res = float(mask_margin_lines[0])
            for valuex_str in mask_margin_lines:
                if mask_margin_res < float(valuex_str):
                    mask_margin_res = float(valuex_str)
        except ValueError:
            mask_margin_res = 'Float_err'
        except IndexError:
            mask_margin_res = 'Index_err'
        return mask_margin_res


    def get_pwr_avg_CMP180(self, is11b=0):
        self.wlan_Adjust_lvl()
        self.wlan_meas_start()
        time.sleep(1)

        if not is11b:
            ms_pwr = self.wlan_meas_pwr()
        else:
            ms_pwr = self.wlan_meas_11b_pwr()
        return ms_pwr


if __name__ == "__main__":
    address = "TCPIP0::10.21.12.184::hislip0::INSTR"
    CMPX = CMP180vs(address)
    # CMPX.wlan_set_route("RF1.7")
    # CMPX.fsq_set_route("RF1.7")
    # CMPX.sa.query("CATalog:GPRF:GEN:SPATh?")

    CMPX.sge_set_route("RF1.1")


    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180vs()
    CMPX.open_tcp(host, port)
    print(CMPX.id_string())
    print(CMPX.wlan_meas_tsmask_max_maxval())
    #print(CMPX.wlan_meas_tsmask_max())
    #print(CMPX.wlan_meas_tsmask_avg())
    #print(CMPX.wlan_meas_11b_avg())
    #print(CMPX.wlan_meas_evm())
    # evm = CMPX.wlan_meas_evm()
    # print(evm)
    #print(CMPX.wlan_meas_pwr())

    CMPX.close()
