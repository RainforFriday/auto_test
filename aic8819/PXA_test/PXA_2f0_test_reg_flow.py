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

    UART2 = Uart(3, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # UART2.sendcmd(f'settx 1')

    # PXA_IP = "TCPIP0::10.21.12.195::hislip0::INSTR"
    PXA_IP = "TCPIP0::K-N9030B-40540::hislip0::INSTR"
    pxa = PXA(PXA_IP)

    # PXA_IP = "TCPIP0::10.21.12.195::hislip0::INSTR"
    # pxa = PXA(PXA_IP)
    # bin_file = "testmode_8819_1029.bin"
    bin_file = "testmode_u02_8819_apc_2g411b_105.bin"

    board = 'D40EN2#4'
    rate = '0 0'
    data_dict = {}

    apc_reg = ApcReg(UART2)

    # # once
    # UART2.sendcmd('reboot')
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
    pxa.set_rb(1)
    pxa.set_vb(3)
    pxa.set_reflvl(20)
    pxa.set_startfreq(1000)
    pxa.set_stopfreq(9000)
    pxa.set_Det()
    pxa.sa.write('TRAC1:TYPE MAXH')

    ch_list = [1, 7, 13]
    for ch in range(1,14):
        UART2.sendcmd(f'setch {ch}')
        time.sleep(2)
        UART2.sendcmd('setrate ' + rate)
        UART2.sendcmd('setintv 2000')
        # UART2.sendcmd('pwrmm 1')

        # pwr_list = [42,58,106,122,138,155]
        # for pwr in range(18, 20, 1):
        for a in range(2):
            print('------------------')
            # UART2.sendcmd(f'setpwr {pwr}')
            UART2.sendcmd('settx 1')

            apc_reg.set_wf_pa_v13_sel_avddrf(a)

            f2_res = pxa.get_quick_next_peak_search(wait=5)
            # mark_pwr1 = str(round(float(tt[1]), 2))
            # mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
            print(f'f2_freq: {f2_res[0]}   f2_pwr: {f2_res[1]}')

            f3_res = pxa.get_mark_max_next()
            print(f'f3_freq: {f3_res[0]}   f3_pwr: {f3_res[1]}')

            f4_res = pxa.get_mark_max_next()

            # data_dict['bin_file'] = bin_file
            data_dict['board'] = board
            data_dict['ch'] = ch
            # data_dict['rate'] = rate

            # data_dict['set_pwr'] = pwr

            data_dict['v13_sel_avddr'] = a
            data_dict['hb_hd3_cbit'] = "/"
            data_dict['lb_hd2_input_cbit'] = "/"
            data_dict['trxsw_hd2_cbit'] = "/"

            data_dict['f2_freq'] = f2_res[0]
            data_dict['f2_pwr'] = f2_res[1]
            data_dict['f3_freq'] = f3_res[0]
            data_dict['f3_pwr'] = f3_res[1]
            data_dict['f4_freq'] = f4_res[0]
            data_dict['f4_pwr'] = f4_res[1]
            UART2.sendcmd(f'settx 0')

            print("保存的数据行：", data_dict)
            save_results(data_dict, file_path)

        for b in range(4, 6):
            print('------------------')
            # UART2.sendcmd(f'setpwr {pwr}')
            UART2.sendcmd('settx 1')
            apc_reg.set_wf_pa_hb_hd3_cbit(b)
            for c in range(8):
                apc_reg.set_wf_pa_lb_hd2_input_cbit(b)
                for d in range(4):
                    apc_reg.set_wf_pa_lb_hd2_input_cbit(b)
                    UART2.sendcmd('settx 1')

                    f2_res = pxa.get_quick_next_peak_search(wait=5)
                    # mark_pwr1 = str(round(float(tt[1]), 2))
                    # mark_freq1 = str(round(float(tt[0]) / 1000000, 2))
                    print(f'f2_freq: {f2_res[0]}   f2_pwr: {f2_res[1]}')

                    f3_res = pxa.get_mark_max_next()
                    print(f'f3_freq: {f3_res[0]}   f3_pwr: {f3_res[1]}')

                    f4_res = pxa.get_mark_max_next()

                    # data_dict['bin_file'] = bin_file
                    data_dict['board'] = board
                    data_dict['ch'] = ch
                    # data_dict['rate'] = rate

                    # data_dict['set_pwr'] = pwr

                    data_dict['v13_sel_avddr'] = a
                    data_dict['hb_hd3_cbit'] = b
                    data_dict['lb_hd2_input_cbit'] = c
                    data_dict['trxsw_hd2_cbit'] = d

                    data_dict['f2_freq'] = f2_res[0]
                    data_dict['f2_pwr'] = f2_res[1]
                    data_dict['f3_freq'] = f3_res[0]
                    data_dict['f3_pwr'] = f3_res[1]
                    data_dict['f4_freq'] = f4_res[0]
                    data_dict['f4_pwr'] = f4_res[1]
                    UART2.sendcmd(f'settx 0')

                    print("保存的数据行：", data_dict)
                    save_results(data_dict, file_path)



    # pxa.set_reflvl(-6)
    UART2.sendcmd(f'settx 0')

    # tt=pxa.query(':FREQ:CENT?\n')
    # print(tt)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")
    # UART2.sendcmd('settx 0')
    UART2.close()

