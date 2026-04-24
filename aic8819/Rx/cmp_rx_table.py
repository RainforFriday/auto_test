from aicintf.uart import *
from aicintf.agilent import *
from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
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
from MsPFM.ms_wf import *



def extract_percentage(data_line):
    """从数据行中提取百分比"""
    # 正则匹配百分比模式：per:XX.XX%
    pattern = r'per:(\d+\.\d+)%'
    match = re.search(pattern, data_line)
    if match:
        percentage = float(match.group(1))
        return percentage
    return None

def ms11b_0M(M=1):
    # 11b
    # ch = 7
    rate = "11b"
    # UARTX.sendcmd(f"setch {ch}")
    time.sleep(2)

    UARTX.sendcmd(f"setbw 0 0")
    # UARTX.sendcmd("settx 0")

    freq = get_freq_by_ch(ch)
    CMPX.sge_arb_set_cfreq(freq)
    CMPX.sge_arb_rep(mode="SINGle")
    CMPX.sge_arb_rep_count()
    # CMPX.sge_arb_on()
    CMPX.sge_arb_list_incre(mode="ACYCles")
    wave = f"11b_{M}M_long_1024.wv"

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


def ms11b_11M():
    # 11b
    # ch = 7
    rate = "11b"
    # UARTX.sendcmd(f"setch {ch}")
    time.sleep(2)

    UARTX.sendcmd(f"setbw 0 0")
    # UARTX.sendcmd("settx 0")

    freq = get_freq_by_ch(ch)
    CMPX.sge_arb_set_cfreq(freq)
    CMPX.sge_arb_rep(mode="SINGle")
    CMPX.sge_arb_rep_count()
    # CMPX.sge_arb_on()
    CMPX.sge_arb_list_incre(mode="ACYCles")
    wave = f"11b_11M_long_1024.wv"

    CMPX.sge_arb_set_wave(wave)
    opt_pwr, per = find_optimal_power(UARTX, CMPX, measure_per, p_min=-100, p_max=-80, target=10, tol=0.2, wait=5)
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
    print(f"fcsok: {fcsok_value}")

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

def test_full_pkg(wait):
    # wait dc finish
    fcsok = 0
    CMPX.sge_arb_set_lvl(-30)
    while fcsok < 700:
        UARTX.sendcmd("stoprxstat")
        UARTX.sendcmd("startrxstat")
        CMPX.sge_arb_on()
        time.sleep(wait)
        ret = UARTX.sendcmd("getrxstat")
        parts = ret.split("fcsok=")[1].split(",")[0]
        fcsok = int(parts)
        print(f"fcsok: {fcsok}")
        if fcsok > 200:
            break


def find_optimal_power(UARTX, CMPX, measure_per, p_min=-98, p_max=-50, target=10, tol=0.5, wait=2):
    """
    快速寻找最优功率灵敏度点 (PER≈10%)

    measure_per: 函数接口, 输入功率dBm，返回对应的PER百分比
    p_min, p_max: 搜索范围
    target: 目标PER百分比
    tol: 功率精度 (dB)
    """

    test_full_pkg(wait)

    high_p = p_max
    low_p = p_min
    per_dict = {}
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

        if 7.2 < per < 10.3:
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

def get_wave():
    if "11ax" in wlan_standard:
        wave = f"{wlan_standard}_{bw}M_mcs{mcs}_1024.wv"
    elif "11b" in wlan_standard:
        speed = get_speed_by_rate(rate)
        wave = f"{wlan_standard}_{speed}M_long_1024.wv"
    elif "11g" in wlan_standard:
        speed = get_speed_by_rate(rate)
        wave = f"{wlan_standard}_{speed}M_1024.wv"
    else:
        wave = f"{wlan_standard}_{bw}M_mcs{mcs}_long_1024.wv"

    return wave


def get_wait_pwrBord():
    if "11b" in wlan_standard:
        if mcs < 3:
            wait_time = 10
        else:
            wait_time = 4
    else:
        if mcs == 0:
            wait_time = 3
        else:
            wait_time = 2


    if "11b" in wlan_standard:
        pmin = -100
        pmax = -80
    elif "11g" in wlan_standard and mcs == 11:
        pmin = -80
        pmax = -70
    else:
        if mcs == 0 or mcs == 4:
            pmin = -100
            pmax = -70
        elif mcs == 7:
            pmin = -80
            pmax = -60
        elif mcs == 9:
            pmin = -70
            pmax = -50
        elif mcs == 11:
            pmin = -70
            pmax = -50
        else:
            pmin = -100
            pmax = -50
        # if mcs == 0:
        #     pmin = -100
        #     pmax = -80
        # else:
        #     pmin = -80
        #     pmax = -50

    return wait_time, pmin, pmax



def rx_test():
    wave = get_wave()
    CMPX.sge_arb_set_wave(wave)
    wait_time, pmin, pmax = get_wait_pwrBord()
    opt_pwr, per = find_optimal_power(UARTX, CMPX, measure_per, p_min=pmin, p_max=pmax, target=10,
                                      tol=0.3, wait=wait_time)
    # print(f'choose pwr: {opt_pwr}   per : {per}')

    CMPX.sge_arb_off()
    UARTX.sendcmd("stoprxstat")

    return opt_pwr, per


if __name__ == "__main__":

    NO = "#1"
    passbin = 1

    # diy pwr, per_brd, tol

    xlsx_path = r'.\Table\rx_TABLE.xlsx'
    # xlsx_path = r'.\Table\cmp_TABLE_pwr.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    # rxfile_path = r'.\data\cmp_8819ERN2B_3_data_rx.xlsx'
    rxfile_path = r'.\data\cmp_8819AILIAN_data_rx_' + current_time + '.xlsx'
    rx_dict = {}
    # loss = 1.5

    # 记录开始时间
    start_time = time.time()

    UARTX = Uart(30, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    bin_file = "testmode22_2026_0226_1534.bin"
    # bin_file = "testmode19_2025_1113_2037.bin"

    if not passbin:
        # once
        UARTX.sendcmd('reboot')
        time.sleep(2)
        bin_file_path = './bin/' + bin_file
        load_bin_X16(UARTX, bin_file_path)
        time.sleep(0.5)

    address = "TCPIP0::10.21.12.198::hislip0::INSTR"
    # address = "TCPIP0::192.168.1.102::hislip0::INSTR"
    CMPX = CMP180vs(address)

    CMPX.sge_arb_rep(mode="SINGle")
    CMPX.sge_arb_rep_count()
    CMPX.sge_arb_list_incre(mode="ACYCles")

    # UARTX.sendcmd(f"setxtalcap 3")


    UARTX.sendcmd("settx 0")

    UARTX.sendcmd("stoprxstat")

    # CMPX.wlan_set_peakpwr(30)
    # CMPX.sa.write("CONFigure:WLAN:MEAS:MEValuation:SCOunt:MODulation 5")
    # ms11b()

    table_lines = WF_MS_TABLE(xlsx_path).read()
    for linex in table_lines:
        db_line = WF_MS_LINE(linex)
        if db_line.enable() not in ["Y", "y", "YES", "yes"]:
            continue

        UARTX.sendcmd(db_line.setbw_ucmd())
        rate = " ".join(db_line.setrate_ucmd().strip().split(" ")[1:])
        bw = " ".join(db_line.setbw_ucmd().strip().split(" ")[1:])
        parts = rate.strip().split()
        mode = parts[0]
        mcs = int(parts[1])


        # set route
        if db_line.route() != "":
            CMPX.sge_set_route(db_line.route())

        wlan_standard = get_wlan_stand_by_rate(rate)

        # print(bw)
        if "0 0" in bw:
            bw = 20
            UARTX.sendcmd(f"setbw 0 0")
        elif "1 1" in bw:
            bw = 40
            UARTX.sendcmd(f"setbw 1 1")
        elif "2 2" in bw:
            bw = 80
            UARTX.sendcmd(f"setbw 2 2")

        for setchx in db_line.l_setch_ucmd():
            ch = setchx.strip().split(" ")[1]
            # CMPX.wlan_set_freq_by_ch(ch)
            UARTX.sendcmd(setchx)
            freq = get_freq_by_ch(ch)
            CMPX.sge_arb_set_cfreq(freq)

            # UARTX.sendcmd(f"setch {ch}")

            time.sleep(2)

            opt_pwr, per = rx_test()

            rx_dict['NO'] = NO
            rx_dict['ANT'] = db_line.ant()
            rx_dict['ch'] = ch
            rx_dict['rate'] = wlan_standard
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













