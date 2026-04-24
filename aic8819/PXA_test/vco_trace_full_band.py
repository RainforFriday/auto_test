# from pyinstr.rs.fsq import *
# from icbasic.aicintf.uart import *
from toolkit.PXA import *
from toolkit.ApcReg import *

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
    UART2.sendcmd('setrate 2 3')
    UART2.sendcmd('settx 1')
    UART2.sendcmd('setintv 100')
    UART2.sendcmd('pwrmm 1')
    pwr = 18
    UART2.sendcmd('setpwr '+str(pwr))

    start_time = time.time()
    


    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    pxa.set_rb(1)
    pxa.set_vb(3)
    # pxa.set_span(50)
    pxa.set_reflvl(20)
    pxa.set_startfreq(1000)
    pxa.set_stopfreq(18000)
    pxa.write(':CALC:MARK:PEAK:TABL:STAT 0')
    pxa.write(':CALC:MARK:PEAK:TABL:STAT 1')
    pxa.write(':CALC:MARK:PEAK:SORT FREQ')

    ch_list = [7, 36, 165]
    for ch in ch_list:
        print('------------------')
        print(f'channel:  {ch}')
        UART2.sendcmd(f'setch {ch}')
        time.sleep(2)

        pxa.write('TRAC1:TYPE WRIT')
        pxa.write('TRAC1:TYPE MAXH')
        time.sleep(30)

        png = r'D:\Data\png\VCO8819_5g_ch'+ str(ch) + "_No_duplex_chip2.png"
        png = r'\\10.21.10.13\share\Data\png\VCO8819_5g_ch'+ str(ch) + "_No_duplex_chip2.png"
        png = r'\\10.21.10.13\share\Data\png\VCO8820_ch'+ str(ch) + "_emission1.png"
        cmd1 = ':MMEM:STOR:SCR "' + png + '"'
        pxa.write(cmd1)



        # # 写入CSV文件
        # with open(file, mode='a+', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     cfreq = set_freq_by_ch(ch)
        #
        #     for rate in rate_list:
        #         # rate = 1
        #         cfreq1 = cfreq * rate
        #         pxa.set_cfreq(cfreq1)
        #         # if rate == 1:
        #         #     pxa.set_reflvl(30)
        #         # else:
        #         #     pxa.set_reflvl(0)
        #         # pxa.set_auto_ref_pwr()
        #         tt = pxa.get_peak_mark(4)
        #         mark_pwr1 = str(round(float(tt[1]), 2))
        #         mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
        #         print(f'pwr1: {mark_pwr1}   freq1: {mark_freq1}')
        #         limit = -50
        #         if float(mark_pwr1) > limit:
        #             print('---------------attention')
        #             print(mark_pwr1, mark_freq1)
        #
        #         results = "{},{:.2f},{},{}".format(ch, rate, mark_freq1, mark_pwr1) + '\n'
        #         csvfile.write(results)

                # writer.writerow([])  # 写入空行



    # pxa.set_reflvl(-6)

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")

    UART2.sendcmd('settx 0')
    UART2.close()

