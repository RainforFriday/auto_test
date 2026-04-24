# from pyinstr.rs.fsq import *
from aicinstr.rs.genericinstrument import *
from aicintf.uart import *
# from icbasic.aicintf.uart import *
from itertools import chain
import pyvisa

import csv
import datetime


def set_freq_by_ch(ch):
    # defalut unit : MHz
    if int(ch) < 15:
        freq = (2407 + 5 * int(ch))
    elif (int(ch) > 30) and (int(ch) < 170):
        freq = (5000 + 5 * int(ch))
    else:
        freq = int(ch)
    # self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq


class PXA(GenericInstrument):
    def __init__(self, address):
        super(GenericInstrument, self).__init__()
        self.sa = self.connect_pxa(address)

    def close(self) -> object:
        if hasattr(self, "sa") and self.sa:
            self.sa.close()
            self.sa = None
        return None  # 和父类保持风格一致

    def __del__(self):
        self.sa.close()

    def connect_pxa(self, address):
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

    def set_analyzer_mode(self):
        self.sa.write(":INIT:SAN")
        return True

    def set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.sa.write("FREQ:CENT {}MHZ".format(cfreq))
        return True

    def get_cfreq(self):
        return self.sa.query("FREQ:CENT?").strip()

    def set_startfreq(self, sfreq):  # startfreq unit is MHz
        self.sa.write("FREQ:START {}MHz".format(sfreq))
        return True

    def set_stopfreq(self, sfreq):  # sfreq unit is MHz
        self.sa.write("FREQ:STOP {}MHz".format(sfreq))
        return True

    def set_rb(self, rb):
        self.sa.write("BAND {}MHz".format(rb))
        return True

    def get_rb(self):
        return self.sa.query("BAND?").strip()

    def set_rb_ratio(self, rat=0.1):  # rat = BW/SPAN
        self.sa.write("BAND:RAT {}".format(rat))
        return True

    def set_vb(self, vb):  # vb = 1HZ --- 30MHz , unit MHz
        self.sa.write("BAND:VID {}MHz".format(vb))
        return True

    def get_vb(self):
        return self.sa.query("BAND:VID?").strip()

    def set_vb_rat(self, rat):  # rat = VideoBandwidth/SPAN
        self.sa.write("BAND:VID:RAT {}".format(rat))
        return True

    def set_span(self, span):   # span unit is MHz
        self.sa.write("FREQ:SPAN {}MHz".format(span))
        return True

    def get_span(self):
        return self.sa.query("FREQ:SPAN?").strip()

    def set_reflvl(self, reflvl):
        self.sa.write("DISP:WIND:TRAC:Y:RLEV {}dBm".format(reflvl))
        return True

    def get_reflvl(self):
        pass
        # return self.sa.write("WIND:TRAC:Y:RLEV?")

    def meas_stat(self):
        pass

    def meas_start(self):
        pass

    def meas_abort(self):
        pass

    def meas_stop(self, unit_no=1):
        pass

    def pwroff(self):
        pass

    def sweep_ctrl(self):
        pass

    def get_trace(self):
        pass

    def show(self):
        pass

    def print_red(self, text):
        print(f"\033[31m{text}\033[0m")

    def set_param(self, cfreq, span=100, rb=100, vb=30):
        pass

    def set_Det(self, det="POSitive"):
        self.sa.write(":SENSe:DETector:TRACe1 "+str(det))

    def set_clear(self):
        self.sa.write("DISP:TRAC1:MODE WRITe")
        time.sleep(1)
        return True

    def set_maxhold(self):
        self.sa.write("DISP:TRAC1:MODE MAXH")
        time.sleep(4)
        return True

    def set_maxhold1(self):
        self.sa.write("DISP:TRAC1:MODE MAXH")
        return True

    def set_mark(self, num, freq):
        self.sa.write(":CALCulate:MARKer{}:X {}MHz".format(num, freq))
        return True

    def get_mark_pwr(self,num):
        mpwr = self.sa.query("CALC:MARK{}:Y?".format(num)).strip().split('\n')[-1]

        mpwr = round(float(mpwr), 2)
        return mpwr


    def get_peak_mark(self, wait_time = 2):
        try:
            # self.sa.write("INIT;*WAI")
            # self.sa.write("*CLS")
            # time.sleep(0.1)
            self.sa.write('TRAC1:TYPE WRIT')
            self.sa.write('TRAC1:TYPE MAXH')
            time.sleep(wait_time)
            self.sa.write("CALC:MARK:MAX:PEAK")
            # self.sa.write("CALC:MARK:COUP:STAT 1")
            self.sa.write("CALC:MARK1:CPS:STAT 1")
            # time.sleep(1)
            # self.sa.write("CALC:MARK:MAX:PEAK")
            end_time = time.time() + 30
            # self.sa.query("*OPC?")  # 阻塞直到操作完成
            # time.sleep(2)

            # 2. 带超时的等待循环
            while time.time() < end_time:
                # ready = self.sa.query("*OPC?\n").strip().split('\n')[-1]
                # if ready == '1':
                    # 3. 获取EVM数据
                try:
                    # self.sa.write("*WAI")
                    # self.sa.write("*CLS")
                    for _ in range(3):
                        mfreq = self.sa.query("CALC:MARK:X?").strip().split('\n')[-1]
                        time.sleep(0.1)

                    # self.sa.write("*WAI")
                    # self.sa.write("*CLS")
                    # self.clear_status()
                    # time.sleep(0.1)
                    for _ in range(3):
                        mpwr = self.sa.query("CALC:MARK:Y?").strip().split('\n')[-1]
                        time.sleep(0.1)
                    # resp = self.sa.query("CALC:MARK:X?;CALC:MARK:Y?")
                    # mfreq, mpwr = resp.split(',')

                    list = [mfreq, mpwr]
                    print('list', list)
                    return list
                except Exception as e:
                    continue
                    # print(f"marker数据失败: {str(e)}")
                    # return [-99.1, -99.1]

                # 避免高频查询
                time.sleep(0.5)

                # 4. 超时处理
            print(f"等待超时(30s)，未收到ready信号")
            return [-99.1, -99.1]

        except Exception as e:
            print('pxa get marker fail !!!!!!!!!!!')
            list = [-99.1, -99.1]
        return list


    def get_peak_mark_until_idle(self, wait_time = 2):
        try:
            self.sa.write('TRAC1:TYPE WRIT')
            self.sa.write('TRAC1:TYPE MAXH')
            time.sleep(wait_time)
            self.sa.write("CALC:MARK:MAX:PEAK")
            self.sa.write("CALC:MARK1:CPS:STAT 1")

            time.sleep(0.4)
            # end_time = time.time() + timeout
            # ready = self.sa.query("STAT:OPER:COND?").strip()
            # # 2. 带超时的等待循环
            # while int(ready) != 0 and time.time() < end_time:
            #     time.sleep(0.1)  # 100ms
            #     ready = self.sa.query("STAT:OPER:COND?").strip()

            mfreq = self.sa.query("CALC:MARK:X?").strip().split('\n')[-1]
            time.sleep(0.2)

            # ready = self.sa.query("STAT:OPER:COND?").strip()
            # while int(ready) != 0 and time.time() < end_time + 5:
            #     time.sleep(0.1)  # 100ms
            #     ready = self.sa.query("STAT:OPER:COND?").strip()

            mpwr = self.sa.query("CALC:MARK:Y?").strip().split('\n')[-1]
            # time.sleep(0.1)
            # resp = self.sa.query("CALC:MARK:X?;CALC:MARK:Y?")
            # mfreq, mpwr = resp.split(',')

            mfreq = round(float(mfreq) / 1e6, 2)
            mpwr = round(float(mpwr), 2)
            list = [mfreq, mpwr]
            print('list:', list)
            return list

        except Exception as e:
            print('pxa get marker fail !!!!!!!!!!!')
            list = [-99.1, -99.1]
        return list

    def get_quick_peak_search(self, wait=3):
        # unit MHz
        self.sa.write('TRAC1:TYPE WRIT')
        self.sa.write('TRAC1:TYPE MAXH')
        time.sleep(wait)
        self.sa.write("CALC:MARK:MAX:PEAK")
        time.sleep(0.2)
        mfreq = self.sa.query("CALC:MARK:X?").strip().split('\n')[-1]
        time.sleep(0.1)
        mpwr = self.sa.query("CALC:MARK:Y?").strip().split('\n')[-1]

        mfreq = round(float(mfreq) / 1e6, 2)
        mpwr = round(float(mpwr), 2)
        list = [mfreq, mpwr]
        # print('list:', list)
        return list

    def get_quick_next_peak_search(self, wait=3):
        self.sa.write('TRAC1:TYPE WRIT')
        self.sa.write('TRAC1:TYPE MAXH')
        time.sleep(wait)
        self.sa.write("CALC:MARK:MAX:PEAK")
        self.sa.write("CALC:MARK:MAX:NEXT")
        time.sleep(0.2)
        mfreq = self.sa.query("CALC:MARK:X?").strip().split('\n')[-1]
        time.sleep(0.1)
        mpwr = self.sa.query("CALC:MARK:Y?").strip().split('\n')[-1]

        mpwr = round(float(mpwr), 2)
        mfreq = round(float(mfreq) / 1000000, 2)
        list = [mfreq, mpwr]
        print('list:', list)
        return list

    def get_mark_max_next(self):
        self.sa.write("CALC:MARK:MAX:NEXT")
        time.sleep(0.5)
        mfreq = self.sa.query("CALC:MARK:X?").strip().split('\n')[-1]
        time.sleep(0.2)
        mpwr = self.sa.query("CALC:MARK:Y?").strip().split('\n')[-1]

        mpwr = round(float(mpwr), 2)
        mfreq = round(float(mfreq) / 1000000, 2)
        list = [mfreq, mpwr]
        print('list:', list)
        return list


    def get_peak_mark_avg(self, N=10):
        x = 0
        y = 0
        num = 0
        for i in range(int(N)):
            x = self.get_peak_mark()[0]
            num = num + 1
            y = y + float(self.get_peak_mark()[1])
            y_avg = y/float(num)
            if abs(float(self.get_peak_mark()[1]) - y_avg) >2:
                print("get mark peak error")
        return [x, y/float(N)]

    def get_mark(self):
        xx = self.sa.query("CALC:MARK:X?").strip()
        yy = self.sa.query("CALC:MARK:Y?").strip()
        return [xx, yy]

    def save_screen(self, png_file):
        # png = r'\\10.21.10.13\share\Data\png\screen_'+ current_time + "_No_duplex1.png"
        cmd1=':MMEM:STOR:SCR "' + png_file + '"'
        self.sa.write(cmd1)

    def save_trace(self, csv_file):
        # csv1 = r'\\10.21.10.13\share\Data\CSV\_' + current_time + "_No_duplex1_trace.csv"
        cmd1 = ':MMEM:STOR:TRAC:DATA TRACE2,"' + csv_file + '"'
        self.sa.write(cmd1)

    def set_marker_center(self):
        self.sa.write('CALC:MARK:SET:CENT')

    def set_auto_ref_pwr(self):
        self.set_reflvl(30)
        time.sleep(1)
        pwr = self.get_quick_peak_search()
        if int(float(pwr)) < 15:
            self.set_reflvl(int(float(pwr)) + 15)
            time.sleep(1)

    def set_wlan_standard(self, standard: object = "11n", bw='0 0') -> object:
        # standard dict
        STANDARD = {"11n": "N", "11b": "BG", "11a": "AG", "11g": "GDO", "11ac": "AC", "11ax": "AX", "11be": "BE"}

        if standard not in STANDARD.keys():
            wlogerror("standard error: {}, should only be 11n/11b/11g".format(standard))
            sys.exit(0)

        if standard == "11b":
            self.sa.write(":SENS:RAD:STAN:WLAN BG")
        elif standard == "11a":
            self.sa.write(":SENS:RAD:STAN:WLAN AG")
        elif standard == "11g":
            self.sa.write(":SENS:RAD:STAN:WLAN GDO")
        else:
            if "0 0" in bw:
                self.sa.write(":SENS:RAD:STAN:WLAN {}".format(STANDARD[standard] + '20'))
            elif "1 1" in bw:
                self.sa.write(":SENS:RAD:STAN:WLAN {}".format(STANDARD[standard] + '40'))
            elif "2 2" in bw:
                self.sa.write(":SENS:RAD:STAN:WLAN {}".format(STANDARD[standard] + '80'))
        return True

    def set_wlan_freq_by_ch(self, ch=1):
        # defalut unit : Hz
        if int(ch) < 15:
            freq = (2407 + 5 * int(ch)) * 1E6
        elif (int(ch) > 30) and (int(ch) < 170):
            freq = (5000 + 5 * int(ch)) * 1E6
        else:
            freq = int(ch) * 1E6
        self.sa.write(":FREQ:CENT {}".format(freq))

    def set_wlan_evm_meas(self):
        # self.sa.write(':INIT:IMM')
        self.sa.write(':INST:SEL WLAN')
        self.sa.write(':CONFigure:EVM:NDEFault')
        self.sa.write(':INIT:CONT 0')
        self.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 0')
        self.sa.write("*CLS")
        # self.sa.write(':CONFigure:EVM')
        # self.sa.write(':INIT:IMM')
        self.sa.write(':TRIG:EVM:SEQ:SOUR RFB')
        self.sa.write(':SENS:EVM:TIME:SLEN 0.01')
        self.sa.write(':SENS:EVM:AVER:COUN 10')
        self.sa.write(':SENS:EVM:AVER:STAT 1')
        self.sa.write(':SENSe:POWer:RF:ATT 35')

    def wlan_meas_result(self, wlan_standard):
        try:
            # self.sa.write("*WAI")
            # self.sa.write("*CLS")
            if wlan_standard != "11b":
                self.sa.write(':SENS:EVM:OPT')
                time.sleep(0.5)
            self.sa.write(':SENS:EVM:AVER:STAT 0')
            time.sleep(0.1)
            self.sa.write(':SENS:EVM:AVER:STAT 1')
            time.sleep(0.5)

            end_time = time.time() + 30
            # self.sa.query("*OPC?")  # 阻塞直到操作完成
            # time.sleep(2)

            # 2. 带超时的等待循环
            while time.time() < end_time:
                # ready = self.sa.query("*OPC?\n").strip()
                # if ready == '1':
                    # 3. 获取EVM数据
                try:
                    for _ in range(3):
                        res_raw = self.sa.query(':FETCh:EVM?').split(',')
                        time.sleep(0.5)
                    # res_raw = self.sa.query(':FETCh:EVM?').split(',')
                    return [round(float(item), 2) for item in res_raw]
                except Exception as e:
                    continue
                    # print(f"数据解析失败: {str(e)}")
                    # res = [-111.1] * 60
                    # return res

                # 避免高频查询
                time.sleep(0.8)

                # 4. 超时处理
            print(f"等待超时(30s)，未收到ready信号")
            return [-111.1] * 60
        except:
            print('pxa fetch fail !!!!!!!!!!!')
            res = [-111.1] * 60
            return res


    def wlan_meas_result_until_idle(self, wlan_standard, timeout=5):
        try:
            if wlan_standard != "11b":
                self.sa.write(':SENS:EVM:OPT')
                time.sleep(0.5)
            # self.sa.write(':SENS:EVM:AVER:STAT 0')
            self.sa.write(':SENS:EVM:AVER:STAT 1')
            time.sleep(0.2)
            self.sa.write(':INIT:REST')
            time.sleep(0.5)

            end_time = time.time() + timeout
            ready = self.sa.query("STAT:OPER:COND?").strip()
            # time.sleep(2)

            # 2. 带超时的等待循环
            while int(ready) != 0 and time.time() < end_time:
                time.sleep(0.1)  # 100ms
                ready = self.sa.query("STAT:OPER:COND?").strip()

            res_raw = self.sa.query(':FETCh:EVM?').split(',')
                # time.sleep(0.5)
            return [round(float(item), 2) for item in res_raw]


        except:
            print('pxa fetch fail !!!!!!!!!!!')
            res = [-111.1] * 60
            return res


    def wlan_meas_11b_evm_peak(self, res):
        try:
            return res[3]
        except:
            return "-100"

    def wlan_meas_11b_evm_rms(self, res):
        try:
            return res[1]
        except:
            return "-100"

    def wlan_meas_11b_pwr(self, res):
        try:
            return res[35]
        except:
            return "-100"

    def wlan_meas_11b_peak_pwr(self, res):
        try:
            return res[37]
        except:
            return "-100"

    def wlan_meas_pwr(self, res):
        try:
            return res[19]
        except:
            return "-100"

    def wlan_meas_peak_pwr(self, res):
        try:
            # print(self.wlan_meas_avg().split(",")[13])
            return res[21]
        except:
            return "-100"

    def wlan_meas_evm(self, res):
        try:
            return res[1]
        except:
            return "-100"

    def wlan_meas_evm_peak(self, res):
        try:
            return res[3]
        except:
            return "-100"

    def wlan_meas_freq_error(self, res):
        try:
            return res[7]
        except:
            return "-100"

    def wlan_meas_clock_error(self, res):
        try:
            return res[9]
        except:
            return "-100"


    def get_pwr_evm_by_stand(self, db_line, wlan_standard, all_res):
        ''''''
        # measure pwr and evm
        if wlan_standard == "11b":
            if db_line.res_pwr():
                ms_pwr = self.wlan_meas_11b_pwr(all_res)
            else:
                ms_pwr = "NA"

            if db_line.res_evm_avg():
                ms_evm_avg = self.wlan_meas_11b_evm_rms(all_res)
            else:
                ms_evm_avg = "NA"

            if db_line.res_evm_peak():
                ms_evm_peak = self.wlan_meas_11b_evm_peak(all_res)
            else:
                ms_evm_peak = "NA"
        else:
            if db_line.res_pwr():
                ms_pwr = self.wlan_meas_pwr(all_res)
            else:
                ms_pwr = "NA"

            if db_line.res_evm_avg():
                ms_evm_avg = self.wlan_meas_evm(all_res)
            else:
                ms_evm_avg = "NA"

            if db_line.res_evm_peak():
                ms_evm_peak = self.wlan_meas_evm_peak(all_res)
            else:
                ms_evm_peak = "NA"
        return ms_pwr, ms_evm_avg, ms_evm_peak

    def set_SAN_meas(self):
        self.sa.write(':INST:SEL SA')
        # self.sa.write(':INITiate:SANalyzer')
        self.sa.write(':CONFigure:SAN:NDEFault')
        self.sa.write(':CONFigure:SAN')
        self.sa.write(':INIT:IMM')



if __name__ == "__main__":

    # UART2 = Uart(8, wr_mode=True)
    # UART2.set_baudrate("921600")
    # UART2.open()

    # pxa = TcpBus()
    # pxa.open(PXA_IP, 5025)
    # pxa.write(':FREQ:STAR?')
    # r = pxa.read().strip()
    # print(r)
    PXA_IP = "TCPIP0::K-N9030B-40540::hislip0::INSTR"

    pxa = PXA(PXA_IP)
    pxa.open_tcp(PXA_IP, 5025)
    print(pxa.id_string())
    # pxa.set_clear()
    # tt=pxa.query(':CALCulate:MARKer:MAXimum:PEAK')
    # tt=pxa.get_mark()

    # file=r'\\10.21.10.13\share\Data\aic8819\aic8819_Tuner_currentTest_5g_'+ current_time + ".csv"

    ## png1 = r"\\10.21.10.13\share\Data\aic8819\_"+ current_time + "_No_duplex1.png"
    png = r'\\10.21.10.13\share\Data\png\VCO8819_5g_ch165_' + "_No_duplex_chip1.png"
    cmd1=':MMEM:STOR:SCR "' + png + '"'
    pxa.write(cmd1)

    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # csv1 = r'\\10.21.10.13\share\Data\CSV\Trace_' + current_time + "_No1.csv"
    # cmd1 = ':MMEM:STOR:TRAC:DATA TRACE1,"' + csv1 + '"'
    # pxa.write(cmd1)

    #
    # spec1 = r'\\10.21.10.13\share\Data\Spectrogram\_' + current_time + "_No_duplex1_Spectrogram.csv"
    # cmd2 = ':MMEM:STOR:RES:SPEC "' + spec1 + '"'
    # pxa.write(cmd2)

    # options = pxa.query('*OPT?')

    pxa.write(':INST:SEL WLAN')
    pxa.write(':CONFigure:EVM:NDEFault')
    pxa.write(':TRIG:EVM:SEQ:SOUR RFB')
    # pxa.write(':SENS:RAD:STAN:WLAN AX20')
    pxa.write(':SENS:RAD:STAN:WLAN BG')
    pxa.write(':FREQ:CENT 2442 MHz')

    pxa.write(':SENS:EVM:TIME:SLEN 0.01')
    pxa.write(':SENS:EVM:AVER:COUN 40')
    pxa.write(':SENS:EVM:AVER:STAT 1')
    pxa.write(':SENSe:POWer:RF:ATT 30')
    pxa.write(':SENS:EVM:OPT')
    time.sleep(3)

    evm_res_raw = pxa.query(':FETCh:EVM?').split(',')
    # evm_res_raw = pxa.query(':READ:EVM?\n').split(',')
    evm_res = [round(float(item), 4) for item in evm_res_raw]

    rms_evm_avg = evm_res[1]
    burst_pwr_avg = evm_res[19]


    pxa.set_span(100)

    start_time = time.time()
    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file = r'./8819/aic8819_Harmonic_scan_' + current_time + ".csv"

    ch_list = range(36,59)
    # ch_list = [42,58,106,122,138,155]
    for ch in ch_list:
        print('------------------')
        print(f'channel:  {ch}')
        UART2.sendcmd(f'setch {ch}')
        time.sleep(1)


        # 写入CSV文件
        with open(file, mode='a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header0 = ['ch'] + ['bits'] + ['pwr1'] + ['freq1'] + ['pwr2'] + ['freq2']
            writer.writerow(header0)
            for bit in chain(range(0, 16, 2), [15]):
                UART2.write_reg_mask("40344048", " 21: 18", bit)
                cfreq=set_freq_by_ch(ch)
                cfreq1 =cfreq*2
                cfreq2 =cfreq*3
                pxa.set_cfreq(cfreq1)
                tt=pxa.get_peak_mark()
                mark_pwr1 = str(round(float(tt[1]), 2))
                mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
                print(f'pwr1: {mark_pwr1}   freq1: {mark_freq1}')

                pxa.set_cfreq(cfreq2)
                tt2 = pxa.get_peak_mark()
                mark_pwr2 = str(round(float(tt2[1]), 2))
                mark_freq2 = str(round(float(tt2[0]) / 1000000, 2))
                print(f'pwr2: {mark_pwr2}   freq2: {mark_freq2}')
                results = "{},{},{},{},{},{}".format(ch, bit ,mark_pwr1, mark_freq1, mark_pwr2, mark_freq2)+'\n'
                csvfile.write(results)
            writer.writerow([])  # 写入空行


    # pxa.set_reflvl(-6)

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")
    UART2.close()

