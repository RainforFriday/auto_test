from MsPFM.msadc import *
from toolkit.ApcReg import *


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

                if deviation > 0.1:  # 10%偏差
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


def find_closest_reg_value(apc_reg, msadc0, val):
    '''

    Args:
        apc_reg: Register operation instance
        val: goal_val

    Returns: Register Value increment

    '''
    n = 32
    mid = 16  # 中间点

    apc_reg.set_wf_vco_core_psw_bit(mid)
    cur_mid = volt_ms_robust_avg2(msadc0, 3)
    print(f'cur_mid: {cur_mid}')

    # apc_reg.set_wf_vco_core_psw_bit(0)
    # cur_min = volt_ms_robust_avg2(msadc0, 3)
    # print(f'cur_min: {cur_min}')
    #
    # apc_reg.set_wf_vco_core_psw_bit(31)
    # cur_max = volt_ms_robust_avg2(msadc0, 3)
    # print(f'cur_max: {cur_max}')


    # # 边界检查
    # if val <= cur_min:
    #     print("cal done! Use minimum value")
    #     return 0, cur_min
    # if val >= cur_max:
    #     print("cal done! Use maximum value")
    #     return (n - 1), cur_max
    if val >= cur_mid:
        # 向右搜索（从mid到30）
        # for i in range(mid, n - 1):
        for i in range(mid - 2, n - 1):
            apc_reg.set_wf_vco_core_psw_bit(i)
            cur_k = volt_ms_robust_avg2(msadc0, 3)
            print(f'cur_{i}:  {cur_k}')
            apc_reg.set_wf_vco_core_psw_bit(i+1)

            cur_k1 = volt_ms_robust_avg2(msadc0, 3)
            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                # closest_k = i if abs(cur_k - val) < abs(cur_k1 - val) else i + 1
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i+1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'choose {closest_k}  ： {closest_cur}')
                return closest_k, closest_cur
            elif i == n - 2:
                print("cal done! Use maximum value")
                return n - 1, cur_k1
    else:
        # 向左搜索（从mid-1到0）
        # for i in range(mid - 1, -1, -1):
        for i in range(mid + 1, -1, -1):
            apc_reg.set_wf_vco_core_psw_bit(i)
            cur_k = volt_ms_robust_avg2(msadc0, 3)
            print(f'cur_{i}:  {cur_k}')
            apc_reg.set_wf_vco_core_psw_bit(i + 1)
            cur_k1 = volt_ms_robust_avg2(msadc0, 3)
            if (cur_k - val) * (cur_k1 - val) <= 0:
                # 比较f[i]和f[i+1]的距离
                if abs(cur_k - val) < abs(cur_k1 - val):
                    closest_k = i
                    closest_cur = cur_k
                else:
                    closest_k = i + 1
                    closest_cur = cur_k1
                print("cal done!!!")
                print(f'choose {closest_k}  ： {closest_cur}')
                return closest_k, closest_cur
            elif i == 0:
                print("cal done! Use minimum value")
                return 0, cur_k  #


def msadc_init(UARTc):
    UARTc.sendcmd('w 40506008 4338000 ')
    UARTc.sendcmd('w 40580018 3 ')
    time.sleep(0.5)

    UARTc.sendcmd('w 40100038 128')
    UARTc.sendcmd('w 4010d008 12003000')
    UARTc.sendcmd('w 4010d00c 0a0ea5e5')
    UARTc.sendcmd('tc 0')

def i_cal_vco():
    UARTc = uart_open(8)
    itgt = 70  # goal current / mA
    UARTc.sendcmd('setch 1')
    time.sleep(2)
    # UARTc.sendcmd('settx 0')

    apc_reg = ApcReg(UARTc)

    msadc0 = MSADC(clk_div=40, acc_mode=1)

    msadc_init(UARTc)
    apc_reg.set_rtc_rg_dcdc_ldo_rf_mode_sel(0)  # before read curr
    apc_reg.set_wf_enable_off()
    apc_reg.set_wf_test_enable_vco(1)
    apc_reg.set_wf_vco_isense_en(1)
    apc_reg.set_wf_vco_isense_volt_div_en(1)
    apc_reg.set_wf_vco_isense_bit(2)
    apc_reg.set_cfg_ana_test_mode(3)
    apc_reg.set_cfg_ana_test_bit(2)

    reg_value, cur_final = find_closest_reg_value(apc_reg, msadc0, itgt)

    apc_reg.set_wf_enable_off()
    apc_reg.set_wf_vco_isense_en(0)

    uart_close()
    return reg_value, cur_final


if __name__ == "__main__":
    reg_value, cur_final = i_cal_vco()
    print(reg_value, cur_final)


