import datetime
# from aic8819.PXA import *
from MsPFM.ms_wf import *
from pyinstr.rs.cmw import *
# from icbasic.aicinstr.rs.cmp180 import *
# from icbasic.aicintf.uart import *
from icbasic.toolkit.CMP180vs import *
from icbasic.toolkit.util import *
import re
import openpyxl
import os

def load_bin_8822(bin_file):
    UARTX.xmodem_load_bin("x 160000", bin_file)
    time.sleep(0.1)
    UARTX.sendcmd("g 160000")
    time.sleep(2.5)

def chip_control(ch, bw):
    UARTX.sendcmd("setch " + str(ch))
    time.sleep(2)
    UARTX.sendcmd("setbw " + str(bw))
    time.sleep(0.2)

def cmw_control(cmw_config, ch1):
    CMW1.sge_cw_set_power(cmw_config["power"])
    freq = 2442
    if 13 >= ch1 >= 1:
        freq = 2412 + (ch1 - 1) * 5
    elif 165 >= ch1 >= 36:
        freq = 5180 + (ch1 - 36) * 5
    else:
        print("channel out of range!!!")
    CMW1.sge_cw_set_cfreq(freq)
    CMW1.sge_cw_pwr_atten(cmw_config["loss"])
    CMW1.sge_cw_pwr_off()

def get_fcsok(xxx):
    # 提取 fcsok 的数值
    match = re.search(r'fcsok=(\d+)', xxx)
    if match:
        fcsok = int(match.group(1))  # 转成数字
        print("提取到的 fcsok =", fcsok)  # 输出 993
    else:
        print("未找到 fcsok")
    return fcsok

# 单次测试函数（测一次，返回 fcsok）
def run_once_test(cmw_config, ch1):
    # 配置
    cmw_control(cmw_config, ch1)
    UARTX.sendcmd("startrxstat")
    time.sleep(0.1)

    # 开信号3秒
    CMW1.sge_cw_pwr_on()
    time.sleep(3)
    CMW1.sge_cw_pwr_off()

    # 停止读取
    UARTX.sendcmd("setrxstop")
    time.sleep(0.1)

    # 获取结果
    xxx = UARTX.sendcmd("getrxstat")
    # print(xxx)
    fcsok = get_fcsok(xxx)
    return fcsok

# ===================== 新增：Excel 初始化 =====================
def init_excel(file_path):
    if not os.path.exists(file_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "RX测试结果"
        headers = ["NO", "ch", "bw", "power", "loss"]
        ws.append(headers)
        wb.save(file_path)

# ===================== 新增：每测完一个通道就保存一行 =====================
def append_row(file_path, row_data):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    ws.append(row_data)
    wb.save(file_path)

if __name__ == "__main__":
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    rxfile_path = fr'.\data\cmw_8822_data_rx_{current_time}.xlsx'

    rx_dict = {}
    # 新增：创建 data 文件夹 + 初始化Excel表头
    os.makedirs(r'.\data', exist_ok=True)
    init_excel(rxfile_path)

    # 记录开始时间
    start_time = time.time()

    UARTX = Uart(18, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    load_bin_flag = 1
    if load_bin_flag == 1:
        bin_file = r"D:\bin\8822\testmode22_2026_0226_1534.bin"
        load_bin_8822(bin_file)

    # address = "TCPIP0::10.21.12.196::hislip0::INSTR"

    host = "10.21.12.196"
    port = 5025
    CMW1 = CMW()
    CMW1.open_tcp(host, port)
    print(CMW1.id_string())

    # cmw500参数配置,NO用来计数，bw用来记录带宽
    config_20bw = {
        "NO": "1",
        "ch": [36, 100, 165],
        "bw": "0 0",
        "power": -90,
        "loss": "0"
    }

    # config_40bw = {
    #     "NO": "1",
    #     "ch": [],
    #     "bw": "1 1",
    #     "power": "-30",
    #     "loss": "-1.5"
    # }

    for ch1 in config_20bw["ch"]:
        print("\n" + "=" * 60)
        print("Current channel is  " + str(ch1))
        print("=" * 60)

        # 每个通道重新从 -30 开始
        current_power = config_20bw["power"]
        final_power = current_power  # 最终记录的功率

        while True:
            print(f"\n--- 当前测试功率：{current_power} dBm ---")
            config_20bw["power"] = current_power
            # 先设置芯片参数
            chip_control(ch1, config_20bw["bw"])
            # 测 3 次，取平均
            fcsok_list = []
            for i in range(3):
                print(f"\n→ 第 {i + 1} 次测试...")
                f = run_once_test(config_20bw, ch1)
                fcsok_list.append(f)
                time.sleep(0.5)

            # 计算平均值
            avg_fcsok = sum(fcsok_list) / 3
            print(f"\n3次平均 fcsok = {avg_fcsok:.1f}")

            # 判断
            if avg_fcsok >= 900:
                print(f"fcsok ≥900，功率-1，重新测试")
                current_power -= 1
            else:
                print(f"fcsok <900，测试结束！")
                final_power = current_power
                break  # 退出while，进入下一个通道

        # 记录当前通道的最终功率
        print(f"\n通道 {ch1} 最终功率 = {final_power} dBm")
        # 新增：立刻写入Excel一行
        row = [
            config_20bw["NO"],
            ch1,
            config_20bw["bw"],
            final_power,
            config_20bw["loss"]
        ]
        append_row(rxfile_path, row)
        print("本条数据已保存到Excel")



