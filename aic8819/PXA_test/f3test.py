# from pyinstr.rs.fsq import *
from aicinstr.rs.genericinstrument import *
from aicintf.uart import *
# from icbasic.aicintf.uart import *
from toolkit.ApcReg import *
from itertools import chain

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
    # self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq


class PXA(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()

    def set_analyzer_mode(self):
        self.write(":INIT:SAN")
        return True

    def set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.write("FREQ:CENT {}MHZ".format(cfreq))
        return True

    def get_cfreq(self):
        return self.query("FREQ:CENT?")

    def set_startfreq(self, sfreq):  # startfreq unit is MHz
        self.write("FREQ:START {}MHz".format(sfreq))
        return True

    def set_stopfreq(self, sfreq):  # sfreq unit is MHz
        self.write("FREQ:STOP {}MHz".format(sfreq))
        return True

    def set_rb(self, rb):
        self.write("BAND {}MHz".format(rb))
        return True

    def get_rb(self):
        return self.query("BAND?")

    def set_rb_ratio(self, rat=0.1):  # rat = BW/SPAN
        self.write("BAND:RAT {}".format(rat))
        return True

    def set_vb(self, vb):  # vb = 1HZ --- 30MHz , unit MHz
        self.write("BAND:VID {}MHz".format(vb))
        return True

    def get_vb(self):
        return self.query("BAND:VID?")

    def set_vb_rat(self, rat):  # rat = VideoBandwidth/SPAN
        self.write("BAND:VID:RAT {}".format(rat))
        return True

    def set_span(self, span):   # span unit is MHz
        self.write("FREQ:SPAN {}MHz".format(span))
        return True

    def get_span(self):
        return self.query("FREQ:SPAN?")

    def set_reflvl(self, reflvl):
        self.write("DISP:WIND:TRAC:Y:RLEV {}dBm".format(reflvl))
        return True

    def get_reflvl(self):
        pass
        # return self.write("WIND:TRAC:Y:RLEV?")

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

    def set_param(self, cfreq, span=100, rb=100, vb=30):
        pass

    def set_Det(self, rat="RMS"):  # rat = VideoBandwidth/SPAN
        self.write("DET "+str(rat))
        return True
    def set_clear(self):
        self.write("DISP:TRAC1:MODE WRITe")
        time.sleep(1)
        return True

    def set_maxhold(self):
        self.write("DISP:TRAC1:MODE MAXH")
        time.sleep(4)
        return True

    def set_maxhold1(self):
        self.write("DISP:TRAC1:MODE MAXH")
        return True
    def get_peak_mark(self):
        self.write('TRAC1:TYPE WRIT')
        self.write('TRAC1:TYPE MAXH')
        time.sleep(3)
        self.write("CALC:MARK:MAX:PEAK")
        # self.write("INIT;*WAI")
        time.sleep(1)
        self.write("CALC:MARK:MAX:PEAK")
        time.sleep(6)
        return [self.query("CALC:MARK:X?"), self.query("CALC:MARK:Y?")]

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
        xx = self.query("CALC:MARK:X?")
        yy = self.query("CALC:MARK:Y?")
        return [xx, yy]






if __name__ == "__main__":

    UART2 = Uart(8, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    PXA_IP = "10.21.10.159"

    # pxa = TcpBus()
    # pxa.open(PXA_IP, 5025)
    # pxa.write(':FREQ:STAR?')
    # r = pxa.read().strip()
    # print(r)
    pxa = PXA()
    pxa.open_tcp(PXA_IP, 5025)
    print(pxa.id_string())
    # tt=pxa.query(':CALCulate:MARKer:MAXimum:PEAK')
    # tt=pxa.get_mark()

    pxa.set_span(100)

    start_time = time.time()
    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file = r'./8819/aic8819_Harmonic_scan_' + current_time + ".csv"

    # ch_list = range(36,59)
    ch_list = range(1,14)
    # ch_list = [42,58,106,122,138,155]
    for ch in ch_list:
        print('------------------')
        print(f'channel:  {ch}')
        UART2.sendcmd(f'setch {ch}')
        time.sleep(1)


        # 写入CSV文件
        with open(file, mode='a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header0 = ['ch'] + ['bits']  + ['pwr3f'] + ['freq3f']
            writer.writerow(header0)
            for bit in chain(range(0, 16, 2), [15]):
                UART2.write_reg_mask("40344048", " 21: 18", bit)
                cfreq=set_freq_by_ch(ch)
                cfreq1 =cfreq*2
                cfreq2 =cfreq*3
                # pxa.set_cfreq(cfreq1)
                # tt=pxa.get_peak_mark()
                # mark_pwr1 = str(round(float(tt[1]), 2))
                # mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
                # print(f'pwr1: {mark_pwr1}   freq1: {mark_freq1}')

                pxa.set_cfreq(cfreq2)
                tt2 = pxa.get_peak_mark()
                mark_pwr2 = str(round(float(tt2[1]), 2))
                mark_freq2 = str(round(float(tt2[0]) / 1000000, 2))
                print(f'pwr2: {mark_pwr2}   freq2: {mark_freq2}')
                results = "{},{},{},{}".format(ch, bit , mark_pwr2, mark_freq2)+'\n'
                csvfile.write(results)
            writer.writerow([])  # 写入空行


    # pxa.set_reflvl(-6)

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")
    UART2.close()

