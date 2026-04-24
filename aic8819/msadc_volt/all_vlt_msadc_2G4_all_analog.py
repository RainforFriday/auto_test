# from MsPFM.aic8819_cal_ipa import *
# from MsPFM.msadc import *
import time

from icbasic.toolkit.util import *
from MsPFM.msadc import MSADC, uart_open
from toolkit.ApcReg import *
from MsPFM.ms_wf import *
import datetime
import csv
from tqdm.notebook import tqdm
# from icbasic.toolkit.util import print_red, verilog_to_int, save_results
from enum import Enum
import utils


class Blocks(Enum):
    PA = "PA"
    DTMX = "DTMX"
    VCO = "VCO"
    RFPLL = "RFPLL"
    MDLL = "MDLL"
    USB = "USB"

    RMX_SUPERHET = "RMX_SUPERHET"
    LNA24G = "LNA24G"
    LNA = "LNA"

    Null = "Null"


class TestCases(Enum):
    TxHB = "WF_TX_HB_ON"
    TxLB = "WF_TX_LB_ON"
    RxHB = "WF_RX_HB_ON"
    RxLB = "WF_RX_LB_ON"
    BtTx = "BT_TX_ON"
    BtRx = "BT_RX_ON"
    BtCt = "BT_COANT"
    BtPl = "BT_PLL_ON"


def get_dc(msadc0):
    raw_dc = msadc0.measure()
    dc1 = (int(raw_dc.split('x')[1], 16) * 1214 / 32896) - 1214
    return round(dc1, 2)


def volt_ms_robust_avg2(msadc0, avg_num=3, max_retries=3):
    """
    计算f(x)的稳健平均值，当单次测量偏差超过10%时重新获取数据

    参数：
        avg_num:
        max_retries: 最大重试次数

    返回：
        平均值, 有效测量次数
    """
    total_retries = 0
    valid_measurements = []

    while len(valid_measurements) < avg_num and total_retries < max_retries:
        # 获取新的一组3次测量
        current_measurements = []
        for _ in range(avg_num):
            current_measurements.append(get_dc(msadc0))
            print(f'Volt_i: {current_measurements[-1]}')

        # 检查偏差
        needs_retry = False
        if len(current_measurements) > 1:
            for i in range(1, len(current_measurements)):
                prev = current_measurements[i - 1]
                curr = current_measurements[i]
                if prev == 0:  # 避免除以零
                    deviation = float('inf')
                else:
                    deviation = abs(curr - prev) / abs(prev)

                if deviation > 0.15:  # 10%偏差
                    print(f"警告：测量偏差 {deviation * 100:.2f}% 超过阈值，重新测量...")
                    needs_retry = True
                    break

        if not needs_retry:
            valid_measurements.extend(current_measurements)

        total_retries += 1

    if not valid_measurements:
        # raise ValueError("无法获取有效测量数据")
        avg = sum(current_measurements) / len(current_measurements)
    else:
        avg = sum(valid_measurements) / len(valid_measurements)
    return round(avg, 3)


# def vco1():
#     with open(filename, 'a+', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#
#         # 1. 写入说明行（单行注释）
#         writer.writerow(["reg_vco"])
#
#     volt_list=[]
#     # apc_reg.set_wf_test_enable_dtmx(0)
#     apc_reg.set_wf_enable_off()
#     apc_reg.set_wf_test_enable_vco(1)
#     apc_reg.set_cfg_ana_test_mode(2)
#     apc_reg.set_cfg_ana_test_bit(1)
#     print('*****reg_vco')
#
#     for a in [0,1]:
#         apc_reg.set_wf_vco_core_reg_lv_mode(a)
#         for b in [0,8,16,31]:
#             apc_reg.set_wf_vco_core_reg_bit(b)
#             volt1 =get_dc(msadc0)
#             volt_list.append(volt1)
#             apc_reg.print_red(volt1)
#
#     with open(filename, 'a+', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(volt_list)
#         writer.writerow([])
#     apc_reg.set_wf_test_enable_vco(0)
#
# def vco2():
#     with open(filename, 'a+', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#
#         # 1. 写入说明行（单行注释）
#         writer.writerow(["vco_buf"])
#
#
#     volt_list=[]
#     # apc_reg.set_wf_test_enable_dtmx(0)
#     apc_reg.set_wf_enable_off()
#     apc_reg.set_wf_test_enable_vco(1)
#     apc_reg.set_cfg_ana_test_mode(2)
#     apc_reg.set_cfg_ana_test_bit(0)
#     print('*****vco_buf')
#
#     apc_reg.set_lo_rsvd_bit_3(0)
#     for a in [0,1,3]:
#         apc_reg.set_wf_vco_buf_reg_hv_mode_bit(a)
#         for b in [0,8,15]:
#             apc_reg.set_wf_vco_buf_reg_bit(b)
#             volt1 =get_dc(msadc0)
#             volt_list.append(volt1)
#             apc_reg.print_red(volt1)
#
#     with open(filename, 'a+', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(volt_list)
#         writer.writerow([])
#     apc_reg.set_wf_test_enable_vco(0)
#
#
# def dtmx1():
#     with open(filename, 'a+', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#
#         # 1. 写入说明行（单行注释）
#         writer.writerow(["dtmx dvdd dll"])
#
#
#     volt_list=[]
#     # apc_reg.set_wf_test_enable_vco(0)
#     apc_reg.set_wf_enable_off()
#     apc_reg.set_wf_test_enable_dtmx(1)
#     apc_reg.set_txon(3)
#     apc_reg.set_rxon(2)
#     apc_reg.set_cfg_ana_test_mode(2)
#     apc_reg.set_cfg_ana_test_bit(5)
#     print('*****dtmx dvdd dll')
#
#     for a in [0,1]:
#         apc_reg.set_wf_trx_rsvd_bit_3(a)
#         for b in [0,8,15]:
#             apc_reg.set_wf_dtmx_logen_dll_reg_vbit(b)
#             volt1 =get_dc(msadc0)
#             volt_list.append(volt1)
#             print(volt1)
#
#     with open(filename, 'a+', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(volt_list)
#         writer.writerow([])
#     apc_reg.set_wf_test_enable_dtmx(0)
#     apc_reg.set_txon(0)
#     apc_reg.set_rxon(0)
#
#
# def dtmx2():
#     with open(filename, 'a+', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#
#         # 1. 写入说明行（单行注释）
#         writer.writerow(["dtmx lo reg"])
#
#
#     volt_list=[]
#     # apc_reg.set_wf_test_enable_vco(0)
#     apc_reg.set_wf_enable_off()
#     apc_reg.set_wf_test_enable_dtmx(1)
#     apc_reg.set_txon(3)
#     apc_reg.set_rxon(2)
#     apc_reg.set_cfg_ana_test_mode(2)
#     apc_reg.set_cfg_ana_test_bit(4)
#     print('*****dtmx lo reg')
#
#     for a in [0, 1]:
#         apc_reg.set_wf_trx_rsvd_bit_3(a)
#         for b in [0,4,7]:
#             apc_reg.set_wf_dtmx_loreg_vbit(b)
#             volt1 =get_dc(msadc0)
#             volt_list.append(volt1)
#             print(volt1)
#
#     with open(filename, 'a+', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(volt_list)
#         writer.writerow([])
#     apc_reg.set_wf_test_enable_dtmx(0)
#     apc_reg.set_txon(0)
#     apc_reg.set_rxon(0)


def vco_isense(filename):
    with open(filename, 'a+', newline='') as file:
        writer = csv.writer(file)
        # writer.writerow(volt_list)
        writer.writerow([])
        writer.writerow(['reg', 'B点电压(mV)', 'C点电压(mV)'])

        apc_reg.set_cfg_ana_test_bit(2)
        apc_reg.set_wf_vco_isense_bit(2)


        for a in range(32):
            # 测量电压
            apc_reg.set_wf_vco_core_psw_bit(a)
            b = get_dc(msadc0)

            # 写入数据行
            writer.writerow([a, b, '\\'])

            print(f"a={a}: B={b:.3f}mV")

        writer.writerow([])
        writer.writerow([])

        apc_reg.set_cfg_ana_test_bit(3)
        apc_reg.set_wf_vco_isense_bit(1)
        for a in range(32):
            # 测量电压
            apc_reg.set_wf_vco_core_psw_bit(a)
            c = get_dc(msadc0)

            # 写入数据行
            writer.writerow([a, '\\', c])

            print(f"a={a}: B={c:.3f}mV")

def tone_on(ch):
    UARTc.sendcmd(f'setch {ch}')
    time.sleep(2)
    UARTc.sendcmd('tone_off')
    time.sleep(0.6)

    UARTc.sendcmd('setrate 5 11')
    UARTc.sendcmd('pwrmm 1')
    # UARTc.sendcmd('setpwr 18')    # 默认A6c pwr13： A79   18：C88
    UARTc.sendcmd('settx 1')
    time.sleep(0.6)
    # UARTc.sendcmd('settx 0')
    # #
    # UARTc.sendcmd('tone_on 0 0')
    UARTc.sendcmd('tc 0')
    time.sleep(0.8)


def tx_on(ch):
    UARTc.sendcmd(f'setch {ch}')
    time.sleep(2)
    UARTc.sendcmd('tone_off')
    time.sleep(0.6)

    UARTc.sendcmd('setrate 5 11')
    UARTc.sendcmd('pwrmm 1')
    UARTc.sendcmd('settx 1')
    time.sleep(0.6)


def tone_on_all_analog():
    for a in range(3):
        for b in range(16):
            if b > 9:
                b = chr(ord("a") + b - 10)

            UARTc.sendcmd(f'tone_on 0 0 {a}{b}')
            print(f'tone_on 0 0 {a}{b}')
            tone_lst = [a, b]
            return tone_lst



def superhet_on():
    apc_reg.set_wf_rmx_super_het_en(1)
    apc_reg.set_wf_pu_rmx_superhet_dr(3)


def superhet_off():
    apc_reg.set_wf_rmx_super_het_en(0)
    apc_reg.set_wf_pu_rmx_superhet_dr(0)


def get_reg_map():
    reg_map = {
        "cm_test_enable_xtal": {"addr": '40505004', "bit": 13},
        "cm_test_enable_mdll": {"addr": '40505004', "bit": 12},

        "cfg_ana_test_enable_usb": {"addr": '40502010', "bit": 4},

        "wf_test_enable_rxflt": {"addr": '4034400c', "bit": 29},
        "wf_test_enable_adc": {"addr": '4034400c', "bit": 28},

        "wf_test_enable_lna5g_preamp": {"addr": '40344008', "bit": 10},
        "wf_test_enable_lna24g": {"addr": '40344008', "bit": 9},
        "wf_test_enable_rmx": {"addr": '40344008', "bit": 8},
        "wf_test_enable_rmx_superhet": {"addr": '40344008', "bit": 7},
        "wf_test_enable_tia": {"addr": '40344008', "bit": 6},
        "wf_test_enable_pa": {"addr": '40344008', "bit": 5},
        "wf_test_enable_dtmx": {"addr": '40344008', "bit": 4},
        "wf_test_enable_iref": {"addr": '40344008', "bit": 3},
        "wf_vco_test_buf_en": {"addr": '40344008', "bit": 2},
        "wf_test_enable_rfpll": {"addr": '40344008', "bit": 1},
        "wf_test_enable_vco": {"addr": '40344008', "bit": 0},

        "bt_test_enable_lna": {"addr": '40622004', "bit": 12},
        "bt_test_enable_vco": {"addr": '40622004', "bit": 5},
        "bt_test_enable_rfpll": {"addr": '40622004', "bit": 6},
        "bt_test_enable_tmx": {"addr": '40622004', "bit": 8},
        "bt_test_enable_pa": {"addr": '40622004', "bit": 7},
        "bt_test_enable_tia": {"addr": '40622004', "bit": 11},
        "bt_test_enable_sdm_adc": {"addr": '40622004', "bit": 10},

    }
    return reg_map


def test():
    print('test')
    # cmdx = '[0x403422C8] = 0x013F4FE8'
    # analog = cmdx.split('=')[1].strip()[-3]

    # reg_map, reg_dict = get_config_from_json('reg_map.json')

    # # 使用示例
    # name = "wf_test_enable_rmx"
    # addr = reg_map[name]["addr"]
    # bit = reg_map[name]["bit"]
    #
    # print(f"{name}: addr=0x{addr:08X}, bit={bit}")


def volt_ms_start_with_cond(enable_filt=1,
                            cond=lambda a, b: (b != Blocks.RMX_SUPERHET.value) & (b != Blocks.LNA24G.value),
                            cond_str=None):
    """
    Modify the table directly without filtering, and then measure all items;
    Recommend using filtering！

    @param cond_str: eval(cond_str), Only choose one between cond and cond_str； eg："block != Blocks.Null.value"
    @param cond: filter function
    @param enable_filt: Whether you need to filter data from the table
    @param case: from Testcase enum
    @param block: from block enum
    """
    data_dict = {}
    reg_map = get_reg_map()
    apc_reg.set_wf_enable_off()

    table_lines = WF_MS_TABLE(xlsx_path).read()
    with tqdm(total=(len(table_lines))) as pbar:
        for linex in table_lines:
            db_line = WF_MS_LINE(linex)
            Test_case = str(db_line.l_line[6]).strip()
            Block = str(db_line.l_line[7]).strip()
            if enable_filt:
                # if block != Block.Null.value:
                # if (block != Block.RMX_SUPERHET.value) & (block != Block.LNA24G.value):
                # if block == Block.LNA24G.value:
                if cond(Test_case, Block):
                    volt_ms_core(db_line, reg_map, data_dict, pbar)
                elif eval(cond_str):
                    volt_ms_core(db_line, reg_map, data_dict, pbar)
            else:
                volt_ms_core(db_line, reg_map, data_dict, pbar)

    # UARTc.sendcmd('tone_off')
    # UARTc.sendcmd('settx 0')
    # superhet_off()
    UARTc.close()


def volt_ms_start(enable_filt=1, case=TestCases.TxHB.value, block=Blocks.DTMX.value, data = [1, 1]):
    """
    Modify the table directly without filtering, and then measure all items;
    Recommend using filtering！

    @param enable_filt: Whether you need to filter data from the table
    @param case: from Testcase enum
    @param block: from block enum
    """
    data_dict = {}
    reg_map = get_reg_map()
    apc_reg.set_wf_enable_off()

    table_lines = WF_MS_TABLE(xlsx_path).read()
    with tqdm(total=(len(table_lines))) as pbar:
        for linex in table_lines:
            db_line = WF_MS_LINE(linex)
            Test_case = str(db_line.l_line[6]).strip()
            Block = str(db_line.l_line[7]).strip()
            if enable_filt:
                # if block != Block.Null.value:
                # if (block != Block.RMX_SUPERHET.value) & (block != Block.LNA24G.value):
                # if block == Block.LNA24G.value:
                # if (Test_case == case) & (Block == block):
                if Block == block:
                    volt_ms_core(db_line, reg_map, data_dict, pbar, data)
            else:
                volt_ms_core(db_line, reg_map, data_dict, pbar, data)

    UARTc.sendcmd('tone_off')
    # UARTc.sendcmd('settx 0')
    # superhet_off()
    UARTc.close()


def volt_ms_core(db_line, reg_map, data_dict, pbar, lst):
    test_enable = str(db_line.l_line[3]).strip()
    mode_str = str(db_line.l_line[4]).strip()
    bit_str = str(db_line.l_line[5]).strip()

    # mode = int(mode_str.split("'b")[1], 2)
    # bit = int(bit_str.split("'b")[1], 2)
    mode = verilog_to_int(mode_str)
    bit = verilog_to_int(bit_str)

    enable_addr = reg_map[test_enable]["addr"]
    enable_bit = reg_map[test_enable]["bit"]

    apc_reg.set_common_enable(enable_addr, enable_bit, 1)
    apc_reg.set_cfg_ana_test_mode(mode)
    apc_reg.set_cfg_ana_test_bit(bit)
    # volt =get_dc(msadc0)
    ms_volt = volt_ms_robust_avg2(msadc0, 2)
    print_red(f"volt： {ms_volt}")

    apc_reg.set_common_enable(enable_addr, enable_bit, 0)

    data_dict["boardno"] = str(db_line.l_line[0]).strip()
    data_dict["bin"] = str(db_line.l_line[1]).strip()
    data_dict["test_enable"] = test_enable
    data_dict["test_mode"] = mode_str
    data_dict["test_bit"] = bit_str
    data_dict["test_case"] = str(db_line.l_line[6]).strip()
    data_dict["function"] = str(db_line.l_line[2]).strip()
    data_dict["rate_table"] = lst[0]
    data_dict["analog"] = lst[1]

    data_dict["volt(mv)"] = round(ms_volt, 2)
    # data_dict["test_case"] = str(db_line.l_line[6]).strip()
    save_results(data_dict, file_path)

    pbar.update(1)
    print(pbar)


if __name__ == "__main__":
    # UARTc.open()
    UARTc = uart_open(3)

    apc_reg = ApcReg(UARTc)
    msadc0 = MSADC(clk_div=40, acc_mode=1)

    UARTc.sendcmd('setch 7')
    time.sleep(3)

    tone_lst = tone_on_all_analog()
    # tone_on(100)
    # superhet_on()
    # apc_reg.set_bt_rxon()

    # enable wlan and rf
    UARTc.sendcmd('w 40506008 4338000 ')
    UARTc.sendcmd('w 40580018 3 ')
    time.sleep(0.5)

    msadc0.ms_portdc_config()

    xlsx_path = r'.\Table\msadc_TABLE_tx_pa.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file_path = r'.\data\msadc_data_2G4_all_analog_' + current_time + '.xlsx'

    volt_ms_start(enable_filt=1, case=TestCases.TxHB.value, block=Blocks.PA.value, data = tone_lst)



