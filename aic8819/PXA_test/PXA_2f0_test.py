# from pyinstr.rs.fsq import *
# from icbasic.aicintf.uart import *
from toolkit.PXA import *
from toolkit.ApcReg import *

import csv
import datetime
from icbasic.toolkit.util import *


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

    UART2 = Uart(18, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # UART2.sendcmd(f'settx 1')

    # PXA_IP = "TCPIP0::10.21.10.124::hislip0::INSTR"
    PXA_IP = "TCPIP0::K-N9030B-40540::hislip0::INSTR"
    pxa = PXA(PXA_IP)
    bin_file = "testmode19_2025_1010_1230.bin"

    board = 'D40E'
    rate = '0 0'
    data_dict = {}

    # # once
    # UARTX.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = './bin/'+bin_file
    # load_bin_X10(UART2, bin_file_path)

    # UART2.sendcmd(f'setch 1')
    # time.sleep(2)
    # UART2.sendcmd('setrate ' + rate)

    # pxa.set_span(100)

    start_time = time.time()
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    file_path = r'.\data\pxa_8819_data_' + current_time + '.xlsx'
    # cfreq = set_freq_by_ch(ch)
    # pxa.set_cfreq(cfreq1)

    ch_list = [1, 7, 13]
    for ch in ch_list:
        UART2.sendcmd(f'setch {ch}')
        time.sleep(2)
        UART2.sendcmd('setrate ' + rate)
        UART2.sendcmd('setintv 500')
        UART2.sendcmd('pwrmm 1')

        # pwr_list = [42,58,106,122,138,155]
        for pwr in range(8, 19, 2):
            print('------------------')
            UART2.sendcmd(f'setpwr {pwr}')
            UART2.sendcmd('settx 1')

            tt = pxa.get_quick_next_peak_search(wait=8)
            mark_pwr1 = str(round(float(tt[1]), 2))
            mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
            print(f'pwr1: {mark_pwr1}   freq1: {mark_freq1}')

            data_dict['bin_file'] = bin_file
            data_dict['board'] = board
            data_dict['ch'] = ch
            data_dict['rate'] = rate

            data_dict['set_pwr'] = pwr
            data_dict['mask_freq'] = mark_freq1
            data_dict['mask_pwr'] = mark_pwr1

            print("保存的数据行：", data_dict)
            save_results(data_dict, file_path)



    # pxa.set_reflvl(-6)

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")
    # UART2.sendcmd('settx 0')
    UART2.close()

