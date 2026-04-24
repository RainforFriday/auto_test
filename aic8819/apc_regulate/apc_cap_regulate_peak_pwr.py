from enum import Enum

# from RsCmwWlanMeas import *
from toolkit.PXA import *

# from MsPFM.msadc import *
from toolkit.ApcReg import *
from toolkit.util import *
import math



def set_MR_table(UARTc, apc_reg):
    mcs = 5
    target = 0
    UARTc.sendcmd(f'setrate 5 {mcs}')
    for _ in range(10):
        rate_table = apc_reg.get_rate_table()  # 假设函数允许传mcs作为输入
        # print(f"当前 MCS={mcs}, rate_table={rate_table}")

        if rate_table == target:
            # print(f"达到目标：MCS={mcs}, rate_table={rate_table}")
            return rate_table

        if rate_table == 2:
            mcs += 1  # 增大 MCS
        elif rate_table == 1:
            mcs -= 1  # 减小 MCS
        else:
            break  # 异常情况

        # 防止超出边界
        mcs = max(0, min(11, mcs))
    print("未达到目标")


if __name__ == "__main__":
    UARTc = uart_open(18)
    apc_reg = ApcReg(UARTc)

    # pwr_limit = 6
    data_dict = {}
    boardno = 4
    bin_ver = 'testmode19_2025_1014_1831.bin'
    # bin_ver = 'testmode19_2025_0818_1550.bin'

    # # once
    # UARTc.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = "./bin/" + bin_ver
    # load_bin_X10(UARTc, bin_file_path)
    # time.sleep(1)

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\apc_regulate\data\apc_data_' + current_time + '.xlsx'
    # file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\apc_regulate\data\apc_data_ch138.xlsx'
    PXA_IP = "TCPIP0::K-N9030B-40540::hislip0::INSTR"
    pxa = PXA(PXA_IP)

    pxa.set_reflvl(30)
    pxa.set_rb(1)
    pxa.set_vb(3)
    pxa.set_span(300)

    test_case = ['CH7_HR', 'CH7_LR',
                 'CH42_MR', 'CH42_HR', 'CH42_LR',
                 'CH58_MR', 'CH58_HR', 'CH58_LR',
                 'CH106_MR', 'CH106_HR', 'CH106_LR',
                 'CH122_MR', 'CH122_HR', 'CH122_LR',
                 'CH138_MR', 'CH138_HR', 'CH138_LR',
                 'CH155_MR', 'CH155_HR', 'CH155_LR']
    rate_group_lst = [0, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]
    ch_group_lst = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]
    UARTc.sendcmd('tc 0')
    UARTc.sendcmd('tone_off')
    apc_reg.release_apc_table_gain()

    # for index in [0] + list(range(3, 20, 3)):
    for index in range(15, 18, 3):
        parts = test_case[index].split('_')
        ch = int(parts[0][2:])
        rate = parts[1]

        UARTc.sendcmd(f'setch {ch}')
        time.sleep(2)
        ch_group = apc_reg.get_txgain_page()
        freq = get_freq_by_ch(ch)

        pxa.set_cfreq(freq)

        start_time = time.time()
        # UARTc.sendcmd('settx 1')

        # analog_char = get_analog_gear(UARTc)
        # analog = int(analog_char, 16)

        analog = 9
        if ch > 7:
            analog = 10


        # Tone on
        # UARTc.sendcmd('tone_on 4 2ff 29')

        # fix_table = rate_table + ch_group * 3
        fix_table = rate_group_lst[index] + ch_group_lst[index] * 3
        fix_table_gain = (fix_table << 4) | analog
        print(hex(fix_table_gain))

        am = "4ff"
        if ch > 7:
            am = "4ff"
        # if index > 14:
        #     am = "4ff"

        UARTc.sendcmd(f'tone_on 4 {am} '+str(hex(fix_table_gain)))

        apc_reg.fix_apc_table_gain(fix_table_gain)
        # assert fix_table == rate_group_lst[index] + ch_group_lst[
        #     index] * 3, f"fix_table unright, index{index}: {fix_table}"
        addrs = get_apc_addr(fix_table, analog)
        addr_high = addrs[1]


        ## 调数字 am代码
        # mk_res = pxa.get_quick_peak_search(wait=2)
        # print(f'pwr: {mk_res[1]}   freq: {mk_res[0]}')
        #
        # UARTc.sendcmd('tone_off')
        #
        # apc_reg.release_apc_table_gain()
        #
        # data_dict["test_case"] = test_case[index]
        # data_dict["am"] = am
        # data_dict["pwrRes"] = mk_res[1]
        # data_dict["frq"] = mk_res[0]
        # print("保存的数据行：", data_dict)
        # save_results(data_dict, file_path)

        data_dict["boardno"] = boardno
        data_dict["bin_version"] = bin_ver
        data_dict["test_case"] = test_case[index]
        data_dict["analog_gear"] = str(analog)
        data_dict["tone_amp"] = am

        if ch > 58:
            in_cbit = 0
            # for in_cbit in range(1, 3):
            apc_reg.set_apc_wf_pa_hb_input_cbit(addr_high, in_cbit)

        for bit in range(32):
        # for bit in [0, 1, 2] + list(range(5, 11, 3)):
        # for bit in range(0, 17, 4):
            if index < 2:
                apc_reg.set_apc_wf_dtmx_cbit_lb(addr_high, bit)
            else:
                apc_reg.set_apc_wf_dtmx_cbit_hb(addr_high, bit)
            mk_res = pxa.get_quick_peak_search(wait=2)
            # print(f'pwr: {mk_res[1]}   freq: {mk_res[0]}')
            data_dict["wf_dtmx_cbit_lb"] = bit
            data_dict["pwrRes"] = mk_res[1]
            data_dict["frq"] = mk_res[0]
            # data_dict["input_cbit"] = in_cbit
            print("保存的数据行：", data_dict)
            save_results(data_dict, file_path)

        apc_reg.release_apc_table_gain()
        UARTc.sendcmd('tone_off')

        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算耗时

        print(f"code spand : {elapsed_time:.2f} s")  # 保留4位小数

        # # data_dict['test_time'] = datetime.datetime.now().strftime("%m%d_%H%M%S")
        # data_dict['test_time'] = elapsed_time
        #
        # print("保存的数据行：", data_dict)
        # save_results(data_dict, file_path)

    UARTc.close()

    # for i in range(28):
    #     UARTc.sendcmd(f'setpwr {i}')
    #     analog_gear = apc_reg.get_analog_gear()
    #     data_dict["setpwr"] = i
    #     data_dict["rate_table"] = analog_gear
    #     print("保存的数据行：", data_dict)
    #     save_results(data_dict, file_path)

    # UARTc.sendcmd(f'setch 7')
    # time.sleep(2)
    # UARTc.sendcmd(f'setlen 2000')
    # for i in range(12):
    #     UARTc.sendcmd(f'setrate 5 {i}')
    #     rate_table = apc_reg.get_rate_table()
    #     data_dict["MCS"] = i
    #     data_dict["rate_table"] = rate_table
    #     print("保存的数据行：", data_dict)
    #     save_results(data_dict, file_path)
