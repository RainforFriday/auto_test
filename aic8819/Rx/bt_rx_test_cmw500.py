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
from cmw_fast_rx_sweep import *

def init_excel(file_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "灵敏度结果"
    headers = ["模式", "速率", "信道", "最终收包数", "总发包数", "灵敏度(dBm)"]
    ws.append(headers)
    wb.save(file_path)

def append_excel(file_path, data):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    ws.append(data)
    wb.save(file_path)

def cmw_control(cmw_config, power, ch1, bt_mode):
    """
    蓝牙信号源控制函数
    :param cmw_config: 功率、损耗配置
    :param ch1: 信道号
    :param bt_mode: 模式标识 -> "ble" 或 "classic"
    """

    # ==================== BLE 模式 ====================
    if bt_mode == "ble":
        # BLE 信道范围 0~39
        if not (0 <= ch1 <= 39):
            raise ValueError(f"BLE 信道超出范围！当前: {ch1}，允许 0~39")

        # BLE 频率公式
        freq = 2402 + ch1 * 2

    # ==================== 经典蓝牙模式 ====================
    elif bt_mode == "classic":
        # 经典蓝牙信道范围 0~78
        if not (0 <= ch1 <= 78):
            raise ValueError(f"经典蓝牙信道超出范围！当前: {ch1}，允许 0~78")

        # 经典蓝牙频率公式
        freq = 2402 + ch1 * 1

    # ==================== 非法模式 ====================
    else:
        raise ValueError(f"不支持的蓝牙模式: {bt_mode}，仅支持 ble / classic")

    # ==================== 正常执行仪器控制 ====================
    CMW1.sge_cw_set_power(power)
    CMW1.sge_cw_set_cfreq(freq)
    CMW1.sge_cw_pwr_atten(cmw_config["loss"])
    CMW1.sge_arb_mode(route="RF1C")
    CMW1.sge_cw_pwr_off()

def get_rx_packet_count(uart):
    rx_result = uart.sendcmd("getrxresult")
    # print(f"\n{rx_result}\n")

    # 提取 po: 后面的数字
    match = re.search(r'BT rx result:\s*(\d+)', str(rx_result))

    if match:
        return int(match.group(1))
    else:
        print("未获取到收包数！")
        return 0


def set_bt_rate(uart, bt_mode, rate, ch):
    """
    测试灵敏度前：自动配置芯片全套串口命令
    :param uart: 串口对象
    :param bt_mode: classic / ble
    :param rate: DH1 / 2DH3 / 3DH5 / BLE1M / BLE2M
    :param ch: 当前测试信道
    """
    print(f"\n========================================")
    print(f"  配置芯片 → {bt_mode} | {rate} | 信道 {ch}")
    print(f"========================================")

    # ==================== 经典蓝牙 ====================
    if bt_mode == "classic":
        # 公共指令
        uart.sendcmd("set_mode 0")
        time.sleep(0.1)

        uart.sendcmd(f"set_chidx {ch}")  # 自动填当前测试信道
        time.sleep(0.1)

        uart.sendcmd("set_pattern 0x00")
        time.sleep(0.1)

        uart.sendcmd("set_addr 0A 1C 6B C6 96 7E")
        time.sleep(0.1)

        # 分包类型配置
        if rate == "DH1":
            uart.sendcmd("set_pkt 0x11")
            uart.sendcmd("set_len 27")

        elif rate == "2DH3":
            uart.sendcmd("set_pkt 0x23")
            uart.sendcmd("set_len 367")

        elif rate == "3DH5":
            uart.sendcmd("set_pkt 0x35")
            uart.sendcmd("set_len 1021")

    # ==================== BLE ====================
    elif bt_mode == "ble":
        # 公共指令
        uart.sendcmd("set_mode 1")
        time.sleep(0.1)

        uart.sendcmd(f"set_chidx {ch}")
        time.sleep(0.1)

        uart.sendcmd("set_pattern 0x00")
        time.sleep(0.1)
        # BLE 你没给 addr，我就不加了，你需要再加

        # 分包类型配置
        if rate == "BLE1M":
            uart.sendcmd("set_pkt 0x41")
            uart.sendcmd("set_len 255")

        elif rate == "BLE2M":
            uart.sendcmd("set_pkt 0x42")
            uart.sendcmd("set_len 255")

    time.sleep(0.5)
    CMW1.arb_file(rate)
    print(f"配置完成：{bt_mode} {rate} 信道 {ch}")


def bt_sensitivity_test(cmw, uart, cmw_config, ch, bt_mode, rate, rxfile_path, total_packet=1000, pass_ratio=0.9, step=-0.5):
    # 单次测试开始时间
    test_st = time.time()

    start_power = cmw_config["power"]
    current_power = start_power
    last_pass_power = current_power
    pass_packet = int(total_packet * pass_ratio)
    final_rx = 0

    # print(f"\n==================================================")
    # print(f"  {bt_mode} | {rate} | 信道 {ch} | 灵敏度测试")
    # print(f"==================================================")

    while True:
        # cmw_config["power"] = current_power
        cmw_control(cmw_config, current_power, ch, bt_mode)

        # print(f"\n当前测试功率: {current_power} dBm")
        uart.sendcmd("setrxstart")
        time.sleep(1)
        cmw.sge_cw_pwr_on()
        if rate == "DH1":
            time.sleep(3)
        elif rate == "3DH5":
            time.sleep(5)
        elif rate == "BLE1M":
            time.sleep(3)
        uart.sendcmd("setrxstop")
        time.sleep(1)
        cmw.sge_cw_pwr_off()
        time.sleep(0.5)

        # print(f"\n当前测试功率: {current_power} dBm")
        uart.sendcmd("setrxstart")
        time.sleep(1)
        cmw.sge_cw_pwr_on()
        if rate == "DH1":
            time.sleep(3)
        elif rate == "3DH5":
            time.sleep(5)
        elif rate == "BLE1M":
            time.sleep(3)
        uart.sendcmd("setrxstop")
        time.sleep(1)
        cmw.sge_cw_pwr_off()
        time.sleep(0.5)

        rx_count = get_rx_packet_count(uart)
        print(f"收包数量: {rx_count} / {total_packet}")

        if rx_count >= pass_packet:
            print(f"功率 {current_power} dBm 测试通过！继续降低功率...")
            last_pass_power = current_power
            final_rx = rx_count  # 这里记录这次通过的收包数（灵敏度对应的收包数）
            current_power = round(current_power + step, 1)
        else:
            print(f"功率 {current_power} dBm 测试不通过！")
            break

        if current_power < -110:
            print("已达到功率下限，停止测试")
            break

    # 计算耗时 → 自动转 时:分:秒
    cost_seconds = time.time() - test_st
    m, s = divmod(cost_seconds, 60)
    h, m = divmod(m, 60)
    time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    print(f"\n第二次结果：【{bt_mode}】{rate} 信道{ch} 灵敏度 = {last_pass_power} dBm")
    print(f"⏱  本次耗时：{time_str}")
    # 实时写入Excel
    append_excel(rxfile_path, [
        bt_mode, rate, ch, final_rx, total_packet, last_pass_power
    ])

    return last_pass_power

if __name__ == "__main__":
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    rxfile_path = fr'.\data\cmw270_8822_data_rx_{current_time}.xlsx'
    os.makedirs(r'.\data', exist_ok=True)
    init_excel(rxfile_path)

    # 记录开始时间
    start_time = time.time()

    host = "10.21.12.188"
    port = 5025
    CMW1 = CMW()
    CMW1.open_tcp(host, port)
    print(CMW1.id_string())

    UARTX = Uart(30, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    # cmw500/270参数配置,NO用来计数，bw用来记录带宽
    config_bt = {
        "NO": "1",
        "loss": 0,
        "test_plan": [  # 自由组合：模式 + 速率 + 任意信道
            {"mode": "classic", "rate": "DH1", "channels": [0, 38]},
            {"mode": "classic", "rate": "3DH5", "channels": [0, 38]},
            {"mode": "ble", "rate": "BLE1M", "channels": [0, 19]},
            # {"mode": "ble", "rate": "BLE2M", "channels": [0, 38]},
        ]

    }


    all_results = []

    # 自动遍历测试
    for item in config_bt["test_plan"]:
        mode = item["mode"]
        rate = item["rate"]
        channels = item["channels"]
        #对不同rate设置不同初始功率
        if item["rate"] == "DH1":
            config_bt["power"] = -92
        elif item["rate"] == "3DH5":
            config_bt["power"] = -50
        elif item["rate"] == "BLE1M":
            config_bt["power"] = -96

        for ch in channels:
            #测之前自动配置芯片
            set_bt_rate(UARTX, mode, rate, ch)
            sens = bt_sensitivity_test(
                cmw=CMW1,
                uart=UARTX,
                cmw_config=config_bt,
                ch=ch,
                bt_mode=mode,
                rate=rate,
                rxfile_path=rxfile_path,
                total_packet=1000,
                pass_ratio=0.9,
                step=-0.5
            )
            all_results.append({
                "mode": mode, "rate": rate, "ch": ch, "sens": sens
            })

    # 最终报告
    print("\n\n========== 测试完成 ==========")

    # 总耗时 时:分:秒
    total_seconds = time.time() - start_time
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    total_time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    print(f"\n全部测试总耗时：{total_time_str}")

    CMW1.close()
    UARTX.close()
    print(f"\n全部完成！文件：{rxfile_path}")

