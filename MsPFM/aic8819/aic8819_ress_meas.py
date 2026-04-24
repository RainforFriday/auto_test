from MsPFM.msadc import *
from toolkit.ApcReg import *



### cal_ipa_hb(itgt=60)
#
# def uart_open(comport):
#     global UARTc
#     UARTc = Uart(comport)
#     UARTc.open()
#     return UARTc
#
# def uart_close():
#     UARTc.close()


def volt_ms_robust_avg(avg_num=3, max_retries=4):
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
            current_measurements.append(msadc0.ms_portdc())
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
    return avg


def find_closest_increment(val):
    '''

    Args:
        f:
        val: goal_val

    Returns:

    '''
    n = 64
    mid = 32  # 中间点

    apc_reg.set_wf_pa_vl_calbit(mid)
    cur_mid = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
    print(f'cur_mid: {cur_mid}')

    apc_reg.set_wf_pa_vl_calbit(0)
    cur_min = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
    print(f'cur_min: {cur_min}')

    apc_reg.set_wf_pa_vl_calbit(63)
    cur_max = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
    print(f'cur_max: {cur_max}')


    # 边界检查
    if val <= cur_min:
        print("cal done! Use minimum value")
        return 0 - mid, cur_min  # 返回 -32
    if val >= cur_max:
        print("cal done! Use maximum value")
        return (n - 1) - mid, cur_max  # 返回 31

    # 向右搜索（从mid到62）
    for i in range(mid, n - 1):
        apc_reg.set_wf_pa_vl_calbit(i)
        cur_k = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
        print(f'cur_{i}:  {cur_k}')
        apc_reg.set_wf_pa_vl_calbit(i+1)
        cur_k1 = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
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
            return closest_k - mid, closest_cur

    # 向左搜索（从mid-1到0）
    for i in range(mid - 1, -1, -1):
        apc_reg.set_wf_pa_vl_calbit(i)
        cur_k = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
        print(f'cur_{i}:  {cur_k}')
        apc_reg.set_wf_pa_vl_calbit(i + 1)
        cur_k1 = (volt_ms_robust_avg(3) - cal_ipa_vofst) / res0
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
            return closest_k - mid, closest_cur

    # 默认返回中间点（理论上不会执行到这里）
    # return 0,



if __name__ == "__main__":

    msadc0 = MSADC(clk_div=40, acc_mode=1)
    UARTc=uart_open(8)
    apc_reg = ApcReg(UARTc)

    # res0=0.565
    # itgt=60

    UARTc.sendcmd('setch 7')
    # UARTc.sendcmd('setrate 5 11')
    # UARTc.sendcmd('settx 0')
    # UARTc.sendcmd('tone_on 0 0')
    # time.sleep(0.2)


    apc_reg.fix_apc_low_table_gain()   # high rate table , fix c

    apc_reg.set_wf_pu_dtmx_wf_lb_dr(1)
    apc_reg.set_wf_pu_dtmx_wf_lb_reg(0)

    # msadc0 = MSADC(clk_div=40, acc_mode=1)

    msadc0.ms_portdc_config()
    apc_reg.set_wf_test_enable_pa(1)

    apc_reg.set_wf_pa_isense_en(1)   # isense_en    isense_rbit 4
    msadc0.testmux(3, 0)    #test mode ,bit
    # msadc0.portdc_mode(2)
    # msadc0.portdc_bit(6)

    apc_reg.set_wf_pa_vl_calbit(32)     # Default

    apc_reg.set_wf_isense_input_sel_bit(1)  # isense_input_sel ; 0 for high

    apc_reg.set_pa_lb_gain_en_dr(1)    # pa_hb_gain_en  10
    apc_reg.set_pa_lb_gain_en_reg(0)    # pa_hb_gain_en  10

    cal_ipa_vofst = volt_ms_robust_avg(3)
    print(f'offset_volt:  {cal_ipa_vofst}')

    apc_reg.set_pa_lb_gain_en_reg(1)

    # cal_ipa_v = volt_ms_robust_avg(3)
    # cal_ipa_init = (cal_ipa_v - cal_ipa_vofst) / res0
    incre, cur_final = find_closest_increment(itgt)

    apc_reg.set_wf_pa_vl_calbit(32)     # Default
    apc_reg.release_apc_low_table_gain()
    apc_reg.set_wf_pa_isense_en(0)   # isense_en    isense_rbit
    apc_reg.set_wf_test_enable_pa(0)

    msadc0.testmux(0, 0)    # test mode ,bit
    apc_reg.set_pa_lb_gain_en_dr(0)  # pa_hb_gain_en  00
    apc_reg.set_pa_lb_gain_en_reg(0)

    apc_reg.set_wf_pu_dtmx_wf_lb_dr(0)
    apc_reg.set_wf_pu_dtmx_wf_lb_reg(0)

    # 还差 set 32


    UARTc.sendcmd('tone_off')

    uart_close()




