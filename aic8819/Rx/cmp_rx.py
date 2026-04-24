from aicintf.uart import *
from aicintf.agilent import *
from pyinstr.rs.Tuner import *
from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
import pyvisa as visa
# from aicintf.gpib import *
import time
import csv
import datetime
# from aic8819.PXA import *
from MsPFM.ms_wf import *
# from icbasic.aicinstr.rs.cmp180 import *
# from icbasic.aicintf.uart import *
from icbasic.toolkit.CMP180vs import *
from icbasic.toolkit.util import *


def extract_percentage(data_line):
    """从数据行中提取百分比"""
    # 正则匹配百分比模式：per:XX.XX%
    pattern = r'per:(\d+\.\d+)%'
    match = re.search(pattern, data_line)
    if match:
        percentage = float(match.group(1))
        return percentage
    return None

def ms11b():
    # 11b
    ch = 7
    rate = "11b"
    UARTX.sendcmd(f"setch {ch}")
    time.sleep(2)

    UARTX.sendcmd(f"setbw 0 0")
    # UARTX.sendcmd("settx 0")

    freq = get_freq_by_ch(ch)
    CMPX.sge_arb_set_cfreq(freq)
    CMPX.sge_arb_rep(mode="SINGle")
    CMPX.sge_arb_rep_count()
    # CMPX.sge_arb_on()
    CMPX.sge_arb_list_incre(mode="ACYCles")
    wave = f"11b_1M_long_1024.wv"

    CMPX.sge_arb_set_wave(wave)
    opt_pwr, per = find_optimal_power(UARTX, CMPX, measure_per, p_min=-100, p_max=-95, target=10, tol=0.2, wait=10)
    # print(f'choose pwr: {opt_pwr}   per : {per}')
    CMPX.sge_arb_off()
    UARTX.sendcmd("starrxstop")

    rx_dict['NO'] = NO
    rx_dict['ch'] = ch
    rx_dict['rate'] = rate
    rx_dict['mcs'] = 0
    rx_dict['bw'] = 20
    rx_dict['lvl'] = opt_pwr
    rx_dict['per'] = per

    print("保存的数据行：", rx_dict)
    save_results(rx_dict, rxfile_path)




def measure_per(UARTX, CMPX, wait = 2):
    # time.sleep(1)
    # percentages = []
    UARTX.sendcmd("stoprxstat")
    UARTX.sendcmd("startrxstat")
    CMPX.sge_arb_on()
    time.sleep(wait)
    ret = UARTX.sendcmd("getrxstat")
    parts = ret.split("fcsok=")[1].split(",")[0]
    fcsok_value = int(parts)
    per = 100 - fcsok_value / 10
    UARTX.sendcmd("stoprxstat")

    # start_time = time.time()
    #
    # while time.time() - start_time < duration:
    #     # 读取一行数据
    #     if UARTX.ser.in_waiting > 0:
    #         line = UARTX.ser.readline().decode('utf-8', errors='ignore').strip()
    #         if line:
    #             # print(f"收到数据: {line}")
    #
    #             # 提取百分比
    #             percentage = extract_percentage(line)
    #             if percentage is not None:
    #                 percentages.append(percentage)
    #                 print(f"{pwr}下提取到百分比: {percentage}%")
    #             else:
    #                 percentage = 100
    #                 percentages.append(percentage)
    #                 print(f"{pwr}下提取到百分比: {percentage}%")
    #
    # per = sorted(percentages)[len(percentages)//2]
    return round(per, 2)


def find_optimal_power(UARTX, CMPX, measure_per, p_min=-98, p_max=-50, target=10, tol=0.5, wait=2):
    """
    快速寻找最优功率灵敏度点 (PER≈10%)

    measure_per: 函数接口, 输入功率dBm，返回对应的PER百分比
    p_min, p_max: 搜索范围
    target: 目标PER百分比
    tol: 功率精度 (dB)
    """

    high_p = p_max
    low_p = p_min
    per_dict={}
    while high_p - low_p > tol:
        mid_p = round((low_p + high_p) / 2, 2)
        CMPX.sge_arb_set_lvl(mid_p)
        per = measure_per(UARTX, CMPX, wait=wait)
        per_dict[mid_p] = per
        print(f"{mid_p} 下per: {per}%")

        if per > target:
            low_p = mid_p  # PER 太高 → 增加功率
        else:
            high_p = mid_p  # PER 太低 → 降低功率

        if 8.4 < per < 10.4:
            high_p = mid_p
            break

    # 最佳点
    # opt_pwr = round((low_p + high_p) / 2, 2) + tol/2
    opt_pwr = high_p
    if opt_pwr in per_dict:
        per = per_dict[opt_pwr]
    else:
        CMPX.sge_arb_set_lvl(opt_pwr)
        per = measure_per(UARTX, CMPX, wait=wait)
        print_red("异常数据，使用边界值")
    print(f'choose pwr: {opt_pwr}   per：{per}')
    return round(opt_pwr, 2), per




if __name__ == "__main__":

    NO = 1

    # xlsx_path = r'.\Table\cmp_TABLE_pwr.xlsx'
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    passbin = 0


    rxfile_path = r'.\data\cmp_8819EN2_2_data_rx.xlsx'
    rx_dict = {}
    # loss = 1.5

    # 记录开始时间
    start_time = time.time()

    UARTX = Uart(17, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    # bin_file = "testmode19_2025_1107_2131.bin"
    # bin_file = "testmode19_2026_0206_1135_g1183bcd-20260205.bin"
    bin_file = "testmode19_2026_0130_1637_ge7e0dfd-20260130.bin"

    if not passbin:
        # # once
        # UARTX.sendcmd('reboot')
        # time.sleep(2)
        bin_file_path = './bin/' + bin_file
        load_bin_X10(UARTX, bin_file_path)
        time.sleep(0.5)

    address = "TCPIP0::10.21.12.185::hislip0::INSTR"
    # address = "TCPIP0::192.168.1.102::hislip0::INSTR"
    CMPX = CMP180vs(address)

    CMPX.sge_set_route("RF1.1")

    # UARTX.sendcmd(f"setxtalcap 3")
    # UARTX.sendcmd("pwrmm 1")
    # UARTX.sendcmd("settx 0")

    # CMPX.wlan_set_peakpwr(30)
    # CMPX.sa.write("CONFigure:WLAN:MEAS:MEValuation:SCOunt:MODulation 5")

    # ms11b()

    # rx
    # ch = 7
    for ch in [7, 42]:
    # for ch in [7]:
        UARTX.sendcmd(f"setch {ch}")
        time.sleep(2)
        # CMPX.sge_set_route("RF1.1")

        # if ch == 7:
        #     CMPX.sge_set_route("RF1.1")
        # else:
        #     CMPX.sge_set_route("RF1.8")
        # for bw in [20, 40, 80]:
        # for bw in [20]:
        # for bw in [40]:
        for bw in [20, 40]:
            if ch == 7 and bw == 80:
                continue

            if bw == 20:
                UARTX.sendcmd(f"setbw 0 0")
            elif bw == 40:
                UARTX.sendcmd(f"setbw 1 1")
            elif bw == 80:
                UARTX.sendcmd(f"setbw 2 2")

            # for mcs in [11]:
            # for mcs in [0]:
            for mcs in [0, 11]:
                # if bw == 80 and mcs == 11:
                #     continue

                if mcs == 0:
                    wait_time = 2
                    pmin = -100
                    pmax = -70
                    # if ch == 7:
                    #     pmin = -88
                    #     pmax = -70
                    #     if bw == 40:
                    #         pmin = -92
                    #         pmax = -81
                    # else:
                    #     # 42 0
                    #     pmin = -95
                    #     pmax = -86
                    #     if bw == 40:
                    #         pmin = -93
                    #         pmax = -86
                elif mcs == 11:
                    wait_time = 1.2
                    pmin = -75
                    pmax = -40
                    # if ch == 7:
                    #     pmin = -70
                    #     pmax = -58
                    #     if bw == 40:
                    #         pmin = -68
                    #         pmax = -55
                    # else:
                    #     # 42 11
                    #     pmin = -70
                    #     pmax = -55
                    #     if bw == 40:
                    #         pmin = -68
                    #         pmax = -42

                # if mcs == 0:
                #     wait_time = 2
                #     if ch == 7:
                #         pmin = -90
                #         pmax = -75
                #     else:
                #         pmin = -95
                #         pmax = -85
                # elif mcs == 11:
                #     wait_time = 1.3
                #     if ch == 7:
                #         pmin = -65
                #         pmax = -45
                #     else:
                #         pmin = -65
                #         pmax = -55
                    # pmin = -70
                    # pmax = -30

                rate = "11ax"

                freq = get_freq_by_ch(ch)
                CMPX.sge_arb_set_cfreq(freq)
                CMPX.sge_arb_rep(mode="SINGle")
                CMPX.sge_arb_rep_count()
                # CMPX.sge_arb_on()
                CMPX.sge_arb_list_incre(mode="ACYCles")
                wave = f"11ax_{bw}M_mcs{mcs}_1024.wv"

                CMPX.sge_arb_set_wave(wave)
                opt_pwr, per = find_optimal_power(UARTX, CMPX, measure_per, p_min=pmin, p_max=pmax, target=10,
                                                  tol=0.2, wait=2)
                # print(f'choose pwr: {opt_pwr}   per : {per}')

                CMPX.sge_arb_off()
                UARTX.sendcmd("stoprxstat")

                rx_dict['NO'] = NO
                rx_dict['ch'] = ch
                rx_dict['rate'] = rate
                rx_dict['mcs'] = mcs
                rx_dict['bw'] = bw
                rx_dict['lvl'] = opt_pwr
                rx_dict['per'] = per

                print(rx_dict)
                save_results(rx_dict, rxfile_path)


    # 计算用时
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"{elapsed_time:.3f} s")
    print("------")


    # CMPX.sge_arb_mode(route="RF1.8")
    # bw = 20
    # CMPX.sa.write(f'SOURce:GPRF:GEN:ARB:FILE "/home/instrument/fw/data/waveform/11ax_{bw}M_mcs11_1024.wv"')
    # CMPX.sa.write(f'SOURce:GPRF:GEN:SEQuencer:APOol:FILE "/home/instrument/fw/data/waveform/{wave}"')
    # CMPX.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:SIGNal 0, "@WAVEFORM/{wave}"')
    # CMPX.sa.write(f'SOURce:GPRF:GEN:SEQuencer:LIST:SIGNal "11n_{bw}M_mcs7_long_1024.wv"')

    # print(aa)

    # CMPX.sa.write("SOURce:GPRF:GEN:BBMode ARB")
    # CMPX.sge_cw_pwr_on()




# SU
#                 if mcs == 0:
#                     wait_time = 2
#                     if ch == 7:
#                         pmin = -88
#                         pmax = -81
#                         if bw == 40:
#                             pmin = -87
#                             pmax = -79.5
#                     else:
#                         pmin = -94
#                         pmax = -89
#                         if bw == 40:
#                             pmin = -91
#                             pmax = -90
#                 elif mcs == 11:
#                     wait_time = 1.2
#                     if ch == 7:
#                         pmin = -61.5
#                         pmax = -53
#                         if bw == 40:
#                             pmin = -58
#                     else:
#                         pmin = -64
#                         pmax = -59
#                         if bw == 40:
#                             pmin = -61
#                             pmax = -56


#D80N2
# if mcs == 0:
#     wait_time = 2
#     if ch == 7:
#         pmin = -88
#         pmax = -70
#         # pmax = -79
#         if bw == 40:
#             pmin = -92
#             pmax = -81
#     else:
#         # 42 0
#         pmin = -95
#         pmax = -86
#         if bw == 40:
#             pmin = -93
#             pmax = -86
# elif mcs == 11:
#     wait_time = 1.2
#     if ch == 7:
#         pmin = -70
#         pmax = -58
#         if bw == 40:
#             pmin = -68
#             pmax = -55
#     else:
#         # 42 11
#         pmin = -70
#         pmax = -55
#         if bw == 40:
#             pmin = -68
#             # pmax = -42
#             pmax = -55













