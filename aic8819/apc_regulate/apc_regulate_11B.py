from enum import Enum

from RsCmwWlanMeas import *

# from MsPFM.msadc import *
from toolkit.ApcReg import *
from toolkit.util import *
import math


def find_closest_it_bit(driver, apc_reg, addr, val, is11b=0, with_step=0):
    '''

    Args:
        apc_reg: Register operation instance
        res0: Experience resistance
        val: goal_val,set_pwr
        default: default_reg_val
        delta: experience_step_curr

    Returns: Register Value increment = Choose - default

    '''
    n = 64

    apc_reg.REG_HIGH = addr
    aa = apc_reg.rapc(42, 37)  # int(aa, 2)
    default = int(aa, 2)

    val_def = get_pwr_avg(driver, is11b)
    print(f'cur_default {default}: {val_def}')
    # apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, 20)

    temp = 0
    # default = max(default, 1)
    # default = min(default, 62)
    start = default
    start = max(min(start, n - 2), 1)
    val_start = val_def
    if with_step:
        if default > 30:
            apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, default-13)
            val_def_sub = get_pwr_avg(driver)
            delta = (val_def - val_def_sub) / 13
        else:
            apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, default + 8)
            val_def_add = get_pwr_avg(driver)
            delta = (val_def_add - val_def) / 8

        if abs(val_def - val) > delta * 3:
            if val >= val_def:
                start = math.floor((val - val_def) / delta) + default
            else:
                start = default - math.floor((val_def - val) / delta)
            start = max(min(start, n - 2), 1)
            apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, start)
            val_start = get_pwr_avg(driver, is11b)
            print(f'val_start  {start}: {val_start}')

    if val >= val_start:
        # 向右搜索
        # for i in range(start, n - 1):
        for i in range(start - 1, n - 1):  # 增大搜索时，起步-1
            if temp != 0:
                cur_k = temp
            else:
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, i)
                cur_k = get_pwr_avg(driver, is11b)
            if abs(cur_k - val) < 0.04:  # 防止起步
                return default, i, cur_k

            apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, i + 1)
            cur_k1 = get_pwr_avg(driver, is11b)
            if math.isnan(cur_k1):
                driver.configure.rfSettings.envelopePower.set(30, connector=repcap.Connector.Default)
                cur_k1 = get_pwr_avg(driver, is11b)
                if math.isnan(cur_k1):
                    return default, i + 1, cur_k1
            temp = cur_k1
            print(f'val_{i}:  {cur_k}   val_{i + 1}:  {cur_k1}')
            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                # closest_k = i if abs(cur_k - val) < abs(cur_k1 - val) else i + 1
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i + 1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'It choose {closest_k}  ： {closest_cur}')
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, closest_k)
                return default, closest_k, closest_cur
            elif i == n - 2:
                print("cal done! It Use maximum value")
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, n - 1)
                return default, (n - 1), cur_k1  # 返回 31
    else:
        # 向左搜索（从mid-1到0）
        # for i in range(start - 1, -1, -1):
        for i in range(start, -1, -1):  # 减小搜索时，起步+2
            if temp != 0:
                cur_k1 = temp
            else:
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, i + 1)
                cur_k1 = get_pwr_avg(driver, is11b)
            if abs(cur_k1 - val) < 0.04:
                return default, i + 1, cur_k1

            apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, i)
            cur_k = get_pwr_avg(driver, is11b)
            if math.isnan(cur_k1):
                driver.configure.rfSettings.envelopePower.set(30, connector=repcap.Connector.Default)
                cur_k1 = get_pwr_avg(driver, is11b)
                if math.isnan(cur_k1):
                    return default, i + 1, cur_k1
            print(f'val_{i}:  {cur_k}   val_{i + 1}:  {cur_k1}')
            temp = cur_k

            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i + 1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'It choose {closest_k}  ： {closest_cur}')
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, closest_k)
                return default, closest_k, closest_cur
            elif i == 0:
                print("cal done! It Use minimum value")
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr, 0)
                return default, 0, cur_k  # 返回 -32


def find_closest_ib_bit(driver, apc_reg, addr, val, is11b=0, with_step=0):
    '''

    Args:
        apc_reg: Register operation instance
        cal_ipa_vofst: off Voltage
        res0: Experience resistance
        val: goal_val,set_pwr
        default: default_reg_val
        delta: experience_step_curr

    Returns: default、choose、pwr Value

    '''
    n = 32

    apc_reg.REG_HIGH = addr
    aa = apc_reg.rapc(36, 32)  # int(aa, 2)
    default = int(aa, 2)

    val_def = get_pwr_avg(driver, is11b)
    print(f'cur_default {default}: {val_def}')

    temp = 0
    # default = max(default, 1)
    # default = min(default, 30)

    start = default
    start = max(min(start, n - 2), 1)
    val_start = val_def

    if with_step:
        if default > 15:
            apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, default - 8)
            val_def_sub = get_pwr_avg(driver, is11b)
            delta = (val_def - val_def_sub) / 8
        else:
            apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, default + 8)
            val_def_add = get_pwr_avg(driver, is11b)
            delta = (val_def_add - val_def) / 8

        if abs(val_def - val) > delta * 3:
            if val >= val_def:
                start = math.floor((val - val_def) / delta) + default
            else:
                start = default - math.floor((val_def - val) / delta)
            start = max(min(start, n - 2), 1)
            apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, start)
            val_start = get_pwr_avg(driver, is11b)
            print(f'val_start  {start}: {val_start}')

    if val >= val_start:
        # 向右搜索
        # for i in range(start, n - 1):
        for i in range(start - 1, n - 1):  # 增大搜索时，起步-1
            if temp != 0:
                cur_k = temp
            else:
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, i)
                cur_k = get_pwr_avg(driver, is11b)
            if abs(cur_k - val) < 0.04:  # 防止起步
                return default, i, cur_k

            apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, i+1)
            cur_k1 = get_pwr_avg(driver, is11b)
            if math.isnan(cur_k1):
                driver.configure.rfSettings.envelopePower.set(30, connector=repcap.Connector.Default)
                cur_k1 = get_pwr_avg(driver, is11b)
                if math.isnan(cur_k1):
                    return default, i + 1, cur_k1
            temp = cur_k1
            print(f'val_{i}:  {cur_k}   val_{i + 1}:  {cur_k1}')
            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                # closest_k = i if abs(cur_k - val) < abs(cur_k1 - val) else i + 1
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i + 1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'Ib choose {closest_k}  ： {closest_cur}')
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, closest_k)
                return default, closest_k, closest_cur
            elif i == n - 2:
                print("cal done! Ib Use maximum value")
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, n - 1)
                return default, (n - 1), cur_k1  # 返回 31
    else:
        # 向左搜索（从mid-1到0）
        # for i in range(start - 1, -1, -1):
        for i in range(start, -1, -1):  # 减小搜索时，起步+1
            if temp != 0:
                cur_k1 = temp
            else:
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, i + 1)
                cur_k1 = get_pwr_avg(driver, is11b)
            if abs(cur_k1 - val) < 0.04:
                return default, i + 1, cur_k1

            apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, i)
            cur_k = get_pwr_avg(driver, is11b)
            if math.isnan(cur_k1):
                driver.configure.rfSettings.envelopePower.set(30, connector=repcap.Connector.Default)
                cur_k1 = get_pwr_avg(driver, is11b)
                if math.isnan(cur_k1):
                    return default, i + 1, cur_k1
            print(f'val_{i}:  {cur_k}   val_{i + 1}:  {cur_k1}')
            temp = cur_k

            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i + 1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'Ib choose {closest_k}  ： {closest_cur}')
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, closest_k)
                return default, closest_k, closest_cur
            elif i == 0:
                print("cal done! Ib Use minimum value")
                apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr, 0)
                return default, 0, cur_k  # 返回 -32


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
    UARTc = uart_open(8)
    apc_reg = ApcReg(UARTc)
    pwr_limit = 5
    data_dict = {}
    boardno = 8
    bin_ver = 'testmode_8819_0910.bin'
    # bin_ver = 'testmode19_2025_0818_1550.bin'

    # once
    UARTc.sendcmd('reboot')
    time.sleep(2)
    bin_file_path = "./" + bin_ver
    load_bin_X10(UARTc, bin_file_path)
    time.sleep(3)

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\apc_regulate\data\apc_11B_data_' + current_time + '.xlsx'
    RsCmwWlanMeas.assert_minimum_version('3.8.20')
    resource_string_1 = 'TCPIP0::10.21.10.124::INSTR'
    driver = RsCmwWlanMeas(resource_string_1)
    idn = driver.utilities.query_str('*IDN?')
    print(f"\nHello, I am: '{idn}'")

    test_case = 'CH7_11B'
    # rate_group_lst = [0,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2]
    # ch_group_lst = [0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6]
    # index = 10
    # for index in range(1, 20):
    parts = test_case.split('_')
    ch = int(parts[0][2:])

    rate = parts[1]

    UARTc.sendcmd(f'setch {ch}')
    time.sleep(2)
    ch_group = apc_reg.get_txgain_page()

    driver.configure.isignal.set_standard(enums.IeeeStandard.DSSS)

    driver.configure.isignal.set_bandwidth(bandwidth=enums.Bandwidth.BW20mhz)
    freq = get_freq_by_ch(ch)
    driver.configure.rfSettings.frequency.set_value(frequency=freq * 1e6)
    UARTc.sendcmd('pwrmm 1')
    UARTc.sendcmd("setintv 5000")


    UARTc.sendcmd('setlen 2000')
    UARTc.sendcmd('setrate 0 3')
    UARTc.sendcmd('settx 1')
    rate_table = apc_reg.get_rate_table()
    assert rate_table == 1, f"rate_table != 1, {rate_table}"


    # UARTc.sendcmd('settx 1')
    last_analog = -1  # 上一次的analog，初始化为 -1，确保第一次一定执行

    for setpwr in range(1, 29):  # pwr 1 ~ 24  饱和23.9,
        start_time = time.time()
        UARTc.sendcmd('settx 1')

        UARTc.sendcmd(f'setpwr {setpwr}')
        print(f'setpwr {setpwr}')
        exp_pwr_con = setpwr + 13
        exp_pwr_con = max(min(exp_pwr_con, 30), 25)
        # set expected power
        driver.configure.rfSettings.envelopePower.set(exp_pwr_con, connector=repcap.Connector.Default)

        analog_char = get_analog_gear(UARTc)
        analog = int(analog_char, 16)

        # 如果模拟档位没有增加，跳过当前 pwr
        if analog <= last_analog:
            continue
        last_analog = analog
        # fix_table = rate_table + ch_group * 3
        # assert fix_table == 1, f"fix_table != 1, {fix_table}"
        fix_table = 1
        fix_table_gain = (fix_table << 4) | analog
        apc_reg.fix_apc_table_gain(fix_table_gain)
        addrs = get_apc_addr(fix_table, analog)
        addr_high = addrs[1]

        # get
        it_res0 = find_closest_it_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
        ib_res0 = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
        it_init = it_res0[0]
        ib_init = ib_res0[0]
        it_bit = it_res0[1]
        finish_flag = 0
        for _ in range(12):
            if (ib_res0[1] == 0) & (finish_flag == 0):
                it_bit -= 1
                it_bit, finish_flag = boundary_protect_with_flag(it_bit, 63)
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr_high, it_bit)
                ib_res0 = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
                if finish_flag:
                    break

            elif (ib_res0[1] == 31) & (finish_flag == 0):
                it_bit += 1
                it_bit, finish_flag = boundary_protect_with_flag(it_bit, 63)
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr_high, it_bit)
                ib_res0 = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
                if finish_flag:
                    break
        print_red(f'first choose {it_res0[0]}->{it_bit}     {ib_res0[0]}->{ib_res0[1]}')
        it_first = it_bit
        ib_first = ib_res0[1]

        UARTc.sendcmd('settx 0')
        UARTc.sendcmd(f'setch {ch}')
        time.sleep(2)
        UARTc.sendcmd('settx 1')
        apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr_high, it_first)
        apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit(addr_high, ib_first)

        # it_res = find_closest_it_bit(driver, apc_reg, addr_high, setpwr)
        ib_res = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))    # 2nd 只细调
        apc_reg.REG_HIGH = addr_high
        it_bit = int(apc_reg.rapc(42, 37), 2)  # int(aa, 2)
        finish_flag = 0
        for _ in range(12):
            if (ib_res[1] == 0) & (finish_flag == 0):
                it_bit -= 1
                it_bit, finish_flag = boundary_protect_with_flag(it_bit, 63)
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr_high, it_bit)
                ib_res = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
                if finish_flag:
                    break

            elif (ib_res[1] == 31) & (finish_flag == 0):
                it_bit += 1
                it_bit, finish_flag = boundary_protect_with_flag(it_bit, 63)
                apc_reg.set_apc_wf_dtmx_dac_vl_it_bit(addr_high, it_bit)
                ib_res = find_closest_ib_bit(driver, apc_reg, addr_high, setpwr, is11b=1, with_step=pwr_enable(setpwr, pwr_limit=pwr_limit))
                if finish_flag:
                    break
        print_red(f'second choose {it_bit}     {ib_res[0]}->{ib_res[1]}')
        UARTc.sendcmd('settx 0')

        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算耗时

        print(f"code spand : {elapsed_time:.2f} s")  # 保留4位小数

        # data_dict['test_time'] = datetime.datetime.now().strftime("%m%d_%H%M%S")
        data_dict['test_time'] = elapsed_time
        data_dict["boardno"] = boardno
        data_dict["bin_version"] = bin_ver
        data_dict["test_case"] = test_case
        data_dict["analog_gear"] = analog_char
        data_dict["setpwr"] = setpwr
        data_dict["pwrRes"] = round(ib_res[2], 2)
        data_dict["default_it"] = it_init
        data_dict["default_ib"] = ib_init
        data_dict["it_first"] = it_first
        data_dict["ib_first"] = ib_first
        data_dict["wf_dtmx_dac_vl_it_bit"] = it_bit
        data_dict["wf_dtmx_dac_vl_ib_bit"] = ib_res[1]

        print("保存的数据行：", data_dict)
        save_results(data_dict, file_path)


        # 如果 analog 已经到 0xF，执行完当前 pwr 后退出
        if analog == 15:
            break


    # apc_reg.REG_HIGH = '40348554'
    # aa = apc_reg.rapc(42, 37)  # int(aa, 2)
    # print(int(aa, 2))
    # apc_reg.set_apc_wf_dtmx_dac_vl_it_bit('40348554', 20)
    # apc_reg.set_apc_wf_dtmx_dac_vl_ib_bit('40348554', 15)
    driver.close()
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