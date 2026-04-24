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


def extract_percentage1(data_line):
    """从数据行中提取百分比"""
    # 正则匹配百分比模式：per:XX.XX%
    pattern = r'per:(\d+\.\d+)%'
    match = re.search(pattern, data_line)
    if match:
        percentage = float(match.group(1))
        return percentage
    return None


def measure_per1(UARTX, pwr, duration=3):
    time.sleep(1)
    percentages = []
    UARTX.sendcmd("setrx")
    start_time = time.time()

    while time.time() - start_time < duration:
        # 读取一行数据
        if UARTX.ser.in_waiting > 0:
            line = UARTX.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # print(f"收到数据: {line}")

                # 提取百分比
                percentage = extract_percentage(line)
                if percentage is not None:
                    percentages.append(percentage)
                    print(f"{pwr}下提取到百分比: {percentage}%")
                else:
                    percentage = 100
                    percentages.append(percentage)
                    print(f"{pwr}下提取到百分比: {percentage}%")

    per = sorted(percentages)[len(percentages)//2]
    return per


def find_optimal_power1(UARTX, CMPX, measure_per, p_min=-98, p_max=-50, target=10, tol=0.5):
    """
    快速寻找最优功率灵敏度点 (PER≈10%)

    measure_per: 函数接口, 输入功率dBm，返回对应的PER百分比
    p_min, p_max: 搜索范围
    target: 目标PER百分比
    tol: 功率精度 (dB)
    """

    # 1. 粗搜索，每2dB步进，找到PER跨过10%的区间
    # step = 2.0
    # p = p_min
    # prev_p, prev_per = None, None
    # while p <= p_max:
    #     per = measure_per(p)
    #     if prev_per is not None:
    #         # 找到跨越10%的区间
    #         if (prev_per > target and per < target) or (prev_per < target and per > target):
    #             low_p, high_p = prev_p, p
    #             break
    #     prev_p, prev_per = p, per
    #     p += step
    # else:
    #     raise ValueError("未找到跨越10% PER 的功率区间")

    # 2. 区间缩小（二分法 + 抖动过滤）


    high_p = p_max
    low_p = p_min
    while high_p - low_p > tol:
        mid_p = (low_p + high_p) / 2
        CMPX.sge_cw_set_power(mid_p)
        per = measure_per(UARTX, mid_p, duration=3)

        if per > target:
            low_p = mid_p  # PER 太高 → 增加功率
        else:
            high_p = mid_p  # PER 太低 → 降低功率

    # 最佳点
    # opt_pwr = round((low_p + high_p) / 2, 2) + tol/2
    opt_pwr = high_p
    print(f'choose pwr: {opt_pwr}')
    CMPX.sge_cw_set_power(opt_pwr)
    per = measure_per(UARTX, opt_pwr, duration=3)
    return opt_pwr, per




if __name__ == "__main__":

    address = "TCPIP0::10.21.12.212::hislip0::INSTR"
    CMPX = CMP180vs(address)
    UARTX = Uart(27, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()


    # rx
    ch = 7
    bw = 20
    # UARTX.sendcmd(f"settx {ch}")
    # time.sleep(1.5)

    # UARTX.sendcmd("settx 0")

    freq = get_freq_by_ch(7)
    CMPX.sge_cw_set_cfreq(freq)
    # CMPX.sge_arb_mode(route="RF1.8")
    # bw = 20
    # CMPX.sa.write(f'SOURce:GPRF:GEN:ARB:FILE "/home/instrument/fw/data/waveform/11ax_{bw}M_mcs11_1024.wv"')
    CMPX.sa.write(f'SOURce:GPRF:GEN1:ARB:FILE "/home/instrument/fw/data/waveform/11n_{bw}M_mcs7_long_1024.wv"')
    # print(aa)

    CMPX.sa.write("SOURce:GPRF:GEN:BBMode ARB")
    CMPX.sge_cw_pwr_on()

    opt_pwr, per = find_optimal_power1(UARTX, CMPX, measure_per1, p_min=-98, p_max=-60, target=10, tol=0.4)
    print(f'choose pwr: {opt_pwr}   per : {per}')

    UARTX.sendcmd("setrxstop")
















