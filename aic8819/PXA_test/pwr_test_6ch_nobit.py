# from pyinstr.rs.fsq import *
# from icbasic.aicintf.uart import *
from toolkit.PXA import *
from toolkit.ApcReg import *

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




if __name__ == "__main__":

    PXA_IP = "10.21.10.166"
    pxa = PXA()
    pxa.open_tcp(PXA_IP, 5025)
    print(pxa.id_string())

    UART2 = Uart(8, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    UART2.sendcmd('setch 7')
    time.sleep(1)
    UART2.sendcmd('setrate 5 0')
    UART2.sendcmd('settx 1')
    UART2.sendcmd('setintv 500')
    UART2.sendcmd('pwrmm 1')

    start_time = time.time()

    # pwr_list=[5,10,15,20]
    pwr_list=[20]
    for pwr in pwr_list:

        UART2.sendcmd('setpwr '+str(pwr))
        current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

        pxa.set_rb(1)
        pxa.set_vb(3)
        pxa.set_span(100)
        pxa.set_reflvl(0)

        # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
        # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
        file = r'./8819/8819Harmon_5G_6ch_' + current_time + ".csv"
        # info = 'pwr20; rate 5 0;testmode_8819h_0730.bin; 2nd board, 1st chip'
        with open(file, mode='a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            info = ['Info:'] + ['pwr'+str(pwr)] + ['rate 5 0'] + ['testmode_8819h_0730.bin'] + ['No.2 board'] + ['intv 500']+ ['No.2 board']+['No.2 chip']+['FIB']

            writer.writerow(info)
            writer.writerow([])  # 写入空行
            header0 = ['ch'] + ['pwr1'] + ['freq1'] + ['pwr2'] + ['freq2']
            writer.writerow(header0)

        bit_n=3
        ch_list = [42,58,106,122,138,155]
        for ch in ch_list:
            print('------------------')
            print(f'channel:  {ch}')
            UART2.sendcmd(f'setch {ch}')
            time.sleep(1)
            # 写入CSV文件
            with open(file, mode='a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # writer.writerow(info)
                # csvfile.write(info)
                # header0 = ['ch'] + ['bits'] + ['pwr1'] + ['freq1'] + ['pwr2'] + ['freq2']
                # writer.writerow(header0)
            # for bit in chain(range(0, 2**bit_n, 2), [2**bit_n-1]):
                # if ch<14:
                #     UART2.write_reg_mask("40344048", " 24: 22", bit)
                # else:
                #     UART2.write_reg_mask("40344048", " 24: 18", bit)
                cfreq = set_freq_by_ch(ch)
                cfreq1 = cfreq * 2
                cfreq2 = cfreq * 3

                pxa.set_cfreq(cfreq1)
                tt = pxa.get_peak_mark()
                mark_pwr1 = str(round(float(tt[1]), 2))
                mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
                print(f'pwr1: {mark_pwr1}   freq1: {mark_freq1}')

                pxa.set_cfreq(cfreq2)
                tt2 = pxa.get_peak_mark()
                mark_pwr2 = str(round(float(tt2[1]), 2))
                mark_freq2 = str(round(float(tt2[0]) / 1000000, 2))
                print(f'pwr2: {mark_pwr2}   freq2: {mark_freq2}')
                results = "{},{},{},{},{}".format(ch,mark_pwr1, mark_freq1, mark_pwr2, mark_freq2) + '\n'
                csvfile.write(results)

                # writer.writerow([])  # 写入空行



    # pxa.set_reflvl(-6)

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")

    UART2.sendcmd('settx 0')
    UART2.close()

