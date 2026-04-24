import datetime
import os
import shutil
import utils
import pandas as pd
import math
import time
import sys
import json
from bunch import Bunch
from loguru import logger
from icbasic.aicintf.uart import *

from tqdm import tqdm
# from rich.progress import track
# from rich.console import Console
# import rich

# def do_something():
#     time.sleep(2)
#     rich.print(":smiley: Hello, world! :thumbs_up::sparkles:")
    # Console.print(":smiley: Hello, world! :thumbs_up::sparkles:")


# def uart_open(comport):
#     global UARTc
#     UARTc = Uart(comport)
#     UARTc.open()
#     return UARTc
#
#
# def uart_close():
#     UARTc.close()

def reset_ch(UARTc, ch):
    UARTc.sendcmd('settx 0')
    UARTc.sendcmd(f'setch {ch}')
    time.sleep(2)
    UARTc.sendcmd('settx 1')

def crt_log(log_path, module_name):
    logger.configure(handlers=[
        {
            "sink": sys.stderr,
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} |<lvl>{level:8}</>| {name} : {module}:{line:4} | <cyan>{extra[module_name]}</> | - <lvl>{message}</>",
            "colorize": True
        },
        {
            "sink": log_path,
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} |{level:8}| {name} : {module}:{line:4} | {extra[module_name]} | - {message}",
            "colorize": False
        },
    ])

    log = logger.bind(module_name=module_name)
    # log.debug("Debug message")

    # logger.add('myloguru.log')
    # logger.info("Info message")
    # logger.warning("Warning message")
    # logger.error("Error message")
    # logger.critical("Critical message")
    return log


def get_config_from_json(json_file):
    """
    将配置文件转换为配置类
    :param json_file: json文件
    :return: 配置信息
    """
    with open(json_file, 'r', encoding='utf-8') as config_file:
        config_dict = json.load(config_file)  # 配置字典
    config = Bunch(config_dict)  # 将配置字典转换为类
    return config, config_dict


def save_config_2_json(json_file, cfg_dict):
    """
     json_file:
     cfg_dict:
    """
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(cfg_dict, f, indent=2, ensure_ascii=False)


def print_red(text):
    print(f"\033[31m{text}\033[0m")


def get_freq_by_ch(ch):
    # defalut unit : MHz
    if int(ch) < 15:
        freq = (2407 + 5 * int(ch))
    elif (int(ch) > 30) and (int(ch) < 170):
        freq = (5000 + 5 * int(ch))
    else:
        freq = int(ch)
    # self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq


def save_results(data_dict, file_path):
    """
    保存测试结果到 CSV 或 Excel 文件，每次写入一行
    data_dict: dict，包含 freq, ch, rate, bw, setpwr, cmdx, ms_pwr, ms_evm_avg, clk_err, mask_abs_min
    file_path: str，保存路径，根据后缀自动选择 CSV 或 Excel
    db_line: 提供 boardno(), ant(), binversion()
    """

    # 转为 DataFrame
    df = pd.DataFrame([data_dict])
    # 判断文件后缀
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        # df.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False, encoding="utf-8-sig")
        if not os.path.exists(file_path):
            df.to_csv(file_path, index=False, mode="w", encoding="utf-8-sig")
        else:
            df.to_csv(file_path, index=False, mode="a", header=False, encoding="utf-8-sig")
    elif ext in [".xls", ".xlsx"]:
        from openpyxl import load_workbook
        if os.path.exists(file_path):
            # 追加写
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                # startrow = writer.sheets["Sheet1"].max_row
                # df.to_excel(writer, index=False, header=False, startrow=startrow)
                existing_df = pd.read_excel(file_path)
                new_df = pd.concat([existing_df, df], ignore_index=True)
                new_df.to_excel(writer, index=False)
        else:
            # 新建文件
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
    else:
        raise ValueError("Unsupported file format: {}".format(ext))


def show_progress(success_count, file_size):
    percent = 100 * success_count / file_size
    width = 50
    show_str = ('[%%-%ds]' % width) % (int(round(width * percent / 100)) * "#")
    print('\r%s %d%%' % (show_str, percent), end='')
    sys.stdout.flush()


def show_progress_time(success_count, file_size, elapsed):
    percent = 100 * success_count / file_size
    width = 50
    show_str = ('[%%-%ds]' % width) % (int(round(width * percent / 100)) * "#")
    # print('\r%s %d%%  time used: %.3f s' % (show_str, percent, elapsed), end='')
    print(f'\r{show_str} {percent}%  time used: {elapsed:.3f} s', end='')


def verilog_to_int(s: str) -> int:
    """
    将 Verilog 风格的字面量字符串（如 "2'b10", "3'h7", "8'd255"）
    转换为 int。
    """
    s = s.strip().lower()  # 去掉空格，统一小写
    if "'b" in s:  # 二进制
        return int(s.split("'b")[1], 2)
    elif "'h" in s:  # 十六进制
        return int(s.split("'h")[1], 16)
    elif "'d" in s:  # 十进制
        return int(s.split("'d")[1], 10)
    elif "'o" in s:  # 八进制
        return int(s.split("'o")[1], 8)
    else:
        raise ValueError(f"无法解析格式: {s}")

def signed2dec(din, width):
    if din > pow(2, width-1):
        dout = din - pow(2, width)
    else:
        dout = din
    return dout


def dec2signed(din, width):
    if din < 0:
        dout = din + pow(2, width)
    else:
        dout = din
    return dout


class aicNum:
    def __init__(self, num=None):
        # global definition
        # base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F]
        # self.base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]
        self.num = num
        self.system = self.system_check()

    def system_check(self):
        if str(self.num).strip().startswith("0X") or str(self.num).strip().startswith("0x"):
            return "HEX"
        elif str(self.num).strip().startswith("0O") or str(self.num).strip().startswith("0o"):
            return "OCT"
        elif str(self.num).strip().startswith("0B") or str(self.num).strip().startswith("0b"):
            return "BIN"
        elif str(self.num).strip().startswith("0D") or str(self.num).strip().startswith("0d"):
            return "DEC"
        elif str.isdecimal(str(self.num).strip()):
            return "DEC"
        else:
            return None

    @property
    def BIN(self):
        if self.system == "HEX":
            return self.hex2bin(self.num)
        elif self.system == "OCT":
            return self.oct2bin(self.num)
        elif self.system == "BIN":
            return self.num
        elif self.system == "DEC":
            return self.dec2bin(self.num)
        else:
            return None

    @property
    def DEC(self):
        if self.system == "HEX":
            return self.hex2dec(self.num)
        elif self.system == "OCT":
            return self.oct2dec(self.num)
        elif self.system == "BIN":
            return self.bin2dec(self.num)
        elif self.system == "DEC":
            return int(self.num)
        else:
            return None

    @property
    def HEX(self):
        if self.system == "HEX":
            return self.num
        elif self.system == "OCT":
            return self.oct2hex(self.num)
        elif self.system == "BIN":
            return self.bin2hex(self.num)
        elif self.system == "DEC":
            return self.dec2hex(self.num)
        else:
            return None

    @property
    def OCT(self):
        if self.system == "HEX":
            return self.hex2oct(self.num)
        elif self.system == "OCT":
            return self.num
        elif self.system == "BIN":
            return self.bin2oct(self.num)
        elif self.system == "DEC":
            return self.dec2oct(self.num)
        else:
            return None

    @staticmethod
    def bin2dec(num):
        return int(num, 2)

    @staticmethod
    def oct2dec(num):
        return int(num, 8)

    @staticmethod
    def hex2dec(num):
        return int(num, 16)

    @staticmethod
    def dec2bin(num):
        return bin(int(num))

    @staticmethod
    def hex2bin(num):
        return bin(int(num, 16))

    @staticmethod
    def oct2bin(num):
        return bin(int(num, 8))

    @staticmethod
    def dec2hex(num):
        return hex(int(num))

    @staticmethod
    def bin2hex(num):
        return hex(int(num, 2))

    @staticmethod
    def oct2hex(num):
        return hex(int(num, 8))

    @staticmethod
    def dec2oct(num):
        return oct(int(num))

    @staticmethod
    def bin2oct(num):
        return oct(int(num, 2))

    @staticmethod
    def hex2oct(num):
        return oct(int(num, 16))


def sort_two_list(list1, list2):
    """
    同时排序列表1和列表2；
    两个列表的对应顺序不变；
    :param list1: 列表1
    :param list2: 列表2
    :return: 排序后的两个列表
    """
    list1, list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
    return list1, list2


def traverse_dir_files(root_dir, ext=None):
    """
    列出文件夹中的文件, 深度遍历
    :param root_dir: 根目录
    :param ext: 后缀名
    :return: [文件路径列表, 文件名称列表]
    """
    names_list = []
    paths_list = []
    for parent, _, fileNames in os.walk(root_dir):
        for name in fileNames:
            if name.startswith('.'):  # 去除隐藏文件
                continue
            if ext:  # 根据后缀名搜索
                if name.endswith(tuple(ext)):
                    names_list.append(name)
                    paths_list.append(os.path.join(parent, name))
            else:
                names_list.append(name)
                paths_list.append(os.path.join(parent, name))
    paths_list, names_list = sort_two_list(paths_list, names_list)
    return paths_list, names_list


def mkdir_if_not_exist(dir_name, is_delete=False):
    """
    创建文件夹
    :param dir_name: 文件夹
    :param is_delete: 是否删除
    :return: 是否成功
    """
    try:
        if is_delete:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(u'[INFO] 文件夹 "%s" 存在, 删除文件夹.' % dir_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(u'[INFO] 文件夹 "%s" 不存在, 创建文件夹.' % dir_name)
        return True
    except Exception as e:
        print('[Exception] %s' % e)
        return False


def timestamp_2_readable(time_stamp):
    """
    时间戳转换为可读时间
    :param time_stamp: 时间戳，当前时间：time.time()
    :return: 可读时间字符串
    """
    return datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')


@logger.catch
def my_function(x, y, z):
    return 1 / (x + y + z)


def add_func(x, y, z):
    try:
        return 1 / (x + y + z)
    except ZeroDivisionError:
        log = crt_log('runtime.log', 'add_function1')
        log.debug("What?! ZeroDivisionError")


def load_bin_X10(UART2, bin_file_path):
    UART2.xmodem_load_bin("x 100000", bin_file_path)
    xxx = UART2.sendcmd("g 100000", wait_time=2)
    print(xxx)


def load_bin_X16(UART2, bin_file_path):
    UART2.xmodem_load_bin("x 160000", bin_file_path)
    xxx = UART2.sendcmd("g 160000", wait_time=2)
    print(xxx)

def get_analog_gear(UART):
    cmdx = UART.sendcmd('r 403422c8')
    # print(cmdx)
    for key_str in [",", "\n", "\r", "aic>"]:
        cmdx = cmdx.replace(key_str, " ")
    analog = cmdx.split('=')[1].strip()[-3]
    return analog


def get_pwr_avg(driver, is11b=0):
    driver.multiEval.stop()
    driver.multiEval.initiate()
    time.sleep(0.8)
    driver.utilities.query_opc()
    if not is11b:
        ResultData = driver.multiEval.modulation.average.fetch()
    else:
        ResultData = driver.multiEval.modulation.dsss.average.fetch()
    pwr = ResultData.Burst_Power
    return pwr


# def get_pwr_avg_11b(driver):
#     driver.multiEval.stop()
#     driver.multiEval.initiate()
#     time.sleep(0.3)
#     driver.utilities.query_opc()
#
#     ResultData = driver.multiEval.modulation.dsss.average.fetch()
#     # # evm=ResultData.Evm
#     # evm = 20 * math.log((ResultData.Evm / 100), 10)
#     pwr = ResultData.Burst_Power
#     return pwr


def get_apc_addr(table: int, gain: int):
    base = 0x40348000
    addr_low = base + table * 0x80 + gain * 0x08
    addr_high = addr_low + 0x04
    return hex(addr_low).split('0x')[1], hex(addr_high).split('0x')[1]


def boundary_protect_with_flag(val, bord):
    """
    边界保护函数（自动裁剪模式）
    :param val: 输入数值
    :param bord: 上边界
    :return: (val, finish_flag)
    """
    # 自动裁剪
    if val < 0:
        val = 0
    elif val > bord:
        val = bord

    # 判断边界标志
    finish_flag = 1 if val == 0 or val == bord else 0
    return val, finish_flag


def pwr_enable(pwr, pwr_limit=3):
    flag = 1
    if pwr <= pwr_limit:
        flag = 0
    return flag


if __name__ == "__main__":

    # for i in tqdm(range(10000)):
    #     time.sleep(0.5)

    fix_table = 10
    analog = 12
    fix_table_gain = (fix_table << 4) | analog

    addrs = get_apc_addr(10, 10)
    addr_high = addrs[1]
    add_func(0, 0, 0)
    # my_function(0, 0, 0)


    p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # # 模拟使用
    # fileSize = 100
    # for i in range(fileSize + 1):
    #     show_progress(i, fileSize)
    #     time.sleep(0.1)  # 模拟工作延迟
    #
    # print("\n完成！")

    mode_str = "4'b1010"
    bit_str1 = "3'b1"
    bit_str2 = "3'h7 "

    print(verilog_to_int(mode_str))  # 2
    print(verilog_to_int(bit_str1))  # 6
    print(verilog_to_int(bit_str2))  # 7
