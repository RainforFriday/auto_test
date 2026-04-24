# from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
# from aicintf.gpib import *

from RsCmwWlanMeas import *
import sys
# from datetime import datetime
sys.path.append("../lib/")
from aic8819.CMW_test.lib import device
# import TX.Jupyter.lib.device

from icbasic.toolkit.util import *

import re

def load_bin(UART2,bin_file_path):
    UART2.xmodem_load_bin("x 160000", bin_file_path)
    xxx = UART2.sendcmd("g 160000")
    print(xxx)

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

def check_clk_err(driver, dut, max_try=3):
    """
    检查 clk_err，尝试修正，最多 max_try 次。
    返回最后一次测得的 clk_err（无论是否成功）。
    """
    clk_err = float('nan')
    try:
        for attempt in range(1, max_try + 1):
            # 获取测量结果
            driver.utilities.query_opc()
            ResultData = driver.multiEval.modulation.average.fetch()
            clk_err = ResultData.Clock_Error
            # print(f"[尝试 {attempt}] clk_err = {clk_err}")

            # 判断是否在范围内
            if -0.9 < clk_err < 0.9:
                # print("✅ 成功：clk_err 在范围内")
                return clk_err  # 提前返回成功值
            else:
                # 不在范围内，计算 cap 并发送指令
                cap = round(clk_err / 2)
                if cap == 0:
                    break
                cmd = f"setxtalcap {cap}\r\n"
                print(f"⚠️ clk_err 超出范围，发送指令: {cmd.strip()}")
                dut.uart.send(cmd)
                driver.multiEval.stop()
                driver.multiEval.initiate()
                device.wait_ms(2000)

        # 如果执行完 max_try 次仍未成功，返回最后的 clk_err
        # driver.multiEval.initiate()
        driver.utilities.query_opc()
        print("❌ 失败：多次尝试后仍未成功")
        return clk_err
    except Exception as e:
        clk_err = float('nan')
        driver.multiEval.stop()
        driver.multiEval.initiate()
        driver.utilities.query_opc()
    return clk_err

def get_limit(driver, wlan_standard):
    ResultData = driver.multiEval.modulation.standardDev.fetch()
    modulation = ResultData.Mod_Type
    if wlan_standard == '11b':
        evm_rms_limit = driver.configure.multiEval.limit.modulation.dsss.get_evm_ems()
        limit = 20 * math.log((evm_rms_limit / 100), 10)
    elif wlan_standard == '11n':
        EvmStruct = driver.configure.multiEval.limit.modulation.htOfdm.get_evm()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmStruct.Evm_Q_1_M_12
        elif modulation == enums.ModulationTypeD._64Q12:
            limit = EvmStruct.Evm_Q_6_M_12
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = EvmStruct.Evm_Q_6_M_34
        else:
            limit = EvmStruct.Evm_Q_6_M_56
    elif wlan_standard == '11a':
        EvmStruct = driver.configure.multiEval.limit.modulation.lofdm.get_evm()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmStruct.Evm_6_M
        elif modulation == enums.ModulationTypeD.BPSK34:
            limit = EvmStruct.Evm_9_M
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmStruct.Evm_12_M
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmStruct.Evm_18_M
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmStruct.Evm_24_M
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = EvmStruct.Evm_36_M
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = EvmStruct.Evm_48_M
        else:
            limit = EvmStruct.Evm_54_M

    elif wlan_standard == '11ac':
        EvmAllStruct = driver.configure.multiEval.limit.modulation.vhtOfdm.get_evm_all()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmAllStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmAllStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmAllStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmAllStruct.Evm_16_Qam_12
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = EvmAllStruct.Evm_16_Qam_34
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = EvmAllStruct.Evm_64_Qam_12
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = EvmAllStruct.Evm_64_Qam_34
        elif modulation == enums.ModulationTypeD._64Q56:
            limit = EvmAllStruct.Evm_64_Qam_56
        elif modulation == enums.ModulationTypeD._256Q34:
            limit = EvmAllStruct.Evm_256_Qam_34
        elif modulation == enums.ModulationTypeD._256Q56:
            limit = EvmAllStruct.Evm_256_Qam_56
        elif modulation == enums.ModulationTypeD._1KQ34:
            limit = EvmAllStruct.Evm_1024_Qam_34
        else:
            limit = EvmAllStruct.Evm_1024_Qam_56
    else:
        ValueStruct = driver.configure.multiEval.limit.modulation.heOfdm.evmAll.get_value()
        if modulation == enums.ModulationTypeD.BPSK14:
            limit = ValueStruct.Evm_Br_14
        elif modulation == enums.ModulationTypeD.BPSK12:
            limit = ValueStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK14:
            limit = ValueStruct.Evm_Qr_14
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = ValueStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = ValueStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q14:
            limit = ValueStruct.Evm_16_Qam_14
        elif modulation == enums.ModulationTypeD._16Q38:
            limit = ValueStruct.Evm_16_Qam_38
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = ValueStruct.Evm_16_Qam_12
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = ValueStruct.Evm_16_Qam_34
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = ValueStruct.Evm_64_Qam_23
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = ValueStruct.Evm_64_Qam_34
        elif modulation == enums.ModulationTypeD._64Q56:
            limit = ValueStruct.Evm_64_Qam_56
        elif modulation == enums.ModulationTypeD._256Q34:
            limit = ValueStruct.Evm_256_Qam_34
        elif modulation == enums.ModulationTypeD._256Q56:
            limit = ValueStruct.Evm_256_Qam_56
        elif modulation == enums.ModulationTypeD._1KQ34:
            limit = ValueStruct.Evm_1024_Qam_34
        else:
            limit = ValueStruct.Evm_1024_Qam_56
    return limit



def loop_bin_test(dut, file_path):
    for loop_idx in range(100):   # 循环 100 次
        start_time = time.time()

        data_dict = {}
        data_dict['test_time'] = datetime.datetime.now().strftime("%m%d_%H%M%S")
        data_dict["boardno"] = 8
        data_dict["bin"] = 'testmode_8819_0904_cal_ipa'

        prt_out = dut.load_bin()   # 返回的输出（可迭代）

        # with open('bin_log.txt', "r", encoding="utf-8") as f:
        #     prt_out = f.readlines()

        matches = []
        with open("bin_log.txt", "a", encoding="utf-8") as f:
            for x in prt_out:
                # print(x)

                # 抓取 incr=数字
                matches = re.findall(r"cal done, incr=(-?\d+)", x)
                # if match:
                #     matches.append(match)
                f.write(x + "\n")
            f.write("\n" * 3)  # 3行空行
            f.write(f'loop: {loop_idx + 1}')
            f.write("-" * 60 + "\n")  # 下划线分隔

        # 保存结果
        dut.uart.send("reboot")
        time.sleep(2)
        if len(matches) >= 1:
            try:
                data_dict["incr_5g"] = int(matches[0])
            except ValueError:
                # 万一不是整数（理论上不太可能），可以跳过或记录为 None
                data_dict["incr_5g"] = None

        if len(matches) >= 2:
            try:
                data_dict["incr_24g"] = int(matches[1])
            except ValueError:
                data_dict["incr_24g"] = None

        print("dict：", data_dict)
        save_results(data_dict, file_path)

        elapsed = time.time() - start_time
        show_progress_time(loop_idx+1, 100, elapsed)
        # print(f"\n\rLoop {loop_idx+1}/100 finished, time used: {elapsed:.3f} s")


if __name__ == "__main__":

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_all_sample.xlsx'
    xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_5G_MaxPwr.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\Tuner_swp_data_20250805.csv'
    # file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\data\cmw_data_'+current_time+'.xlsx'
    file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\data\loop_bin_test.xlsx'

    RsCmwWlanMeas.assert_minimum_version('3.8.20')
    resource_string_1 = 'TCPIP0::10.21.10.124::INSTR'  # Standard LAN connection (also called VXI-11)
    # Initializing the session
    driver = RsCmwWlanMeas(resource_string_1)
    idn = driver.utilities.query_str('*IDN?')
    print(f"\nHello, I am: '{idn}'")


    # UARTX = Uart(8, wr_mode=True)
    # UARTX.set_baudrate("921600")
    # UARTX.open()
    # bb1=UARTX.sendcmd('r 403422c8').split('\r')[1].strip()
    # print(bb1)

    data_pool_8819 = {'utm_bin': r"D:\Aic8800\Code\rf_test\UTM\TX\Pycharm\bin\testmode_8819_0904_cal_ipa.bin",
                      'agc_bin': r"C:\Users\AIC_LAB\jupyter_test\8820\bin\agc_ram.bin",
                      'agc_hex': r"C:\Users\AIC_LAB\jupyter_test\8820\bin\agc_ram.hex",
                      'rf_rx_gain_table': r"C:\Users\AIC_LAB\jupyter_test\8820\rf_table\aic8820t_wf_agc_v1.8.xlsx",
                      'loadx_cmd': "x 100000",
                      'go_cmd': "g 100000",
                      'wr': 'w',
                      'rd': 'r',
                      'dump_st_add': 0x00100000,
                      'dump_len': 32768,
                      'maxim_addr': '403450f8',
                      'fix_gain_dr_cmd': ' 4033c040 10000000',
                      'release_gain_dr_cmd': ' 4033c040 0',
                      'fix_gain_value_addr': ' 4033c044 ',
                      'is_fpga': 0
                      }
    dut = device.dut(data_pool_8819, 'COM4')

    # once
    # prt_out = dut.load_bin()
    # for x in prt_out:
    #     print(x)

    # driver.configure.isignal.set_standard(enums.IeeeStandard.HEOFdm)
    # driver.configure.isignal.set_bandwidth(bandwidth=enums.Bandwidth.BW20mhz)
    # driver.configure.rfSettings.frequency.set_value(frequency=5500 * 1e6)
    # driver.multiEval.initiate()
    # # device.wait_ms(2000)
    # driver.utilities.query_opc()

    loop_bin_test(dut, file_path)
