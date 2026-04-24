from MsPFM.msadc import *
from toolkit.ApcReg import *
import math
from icbasic.toolkit.util import *


### cal_ipa_hb(itgt=60)
#
# def uart_open(comport):
#     global UARTc
#     UARTc = Uart(comport)
#     UARTc.open()
#     return UARTc


def volt_ms_robust_avg(msadc0, avg_num=3, max_retries=4):
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

                if deviation > 0.2:  # 10%偏差
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


def cal_ipa_hb():
    UARTc = uart_open(3)
    res_hb = 0.54

    UARTc.sendcmd('setch 100')
    time.sleep(2)
    # UARTc.sendcmd('tone_off')
    # time.sleep(0.6)

    UARTc.sendcmd('tone_on 0 0 1c')
    time.sleep(0.8)

    apc_reg = ApcReg(UARTc)
    msadc0 = MSADC(clk_div=40, acc_mode=1)
    msadc0.ms_portdc_config()

    # apc_reg.fix_apc_high_table_gain()  # high rate table , fix c

    apc_reg.set_wf_pu_dtmx_wf_hb_dr(1)
    apc_reg.set_wf_pu_dtmx_wf_hb_reg(0)  #

    apc_reg.set_wf_test_enable_pa(1)

    apc_reg.set_wf_pa_isense_en(1)  # isense_en    isense_rbit
    msadc0.testmux(3, 0)  # test mode ,bit

    # apc_reg.set_wf_pa_vl_calbit(default_reg_val)  # Default

    apc_reg.set_wf_isense_input_sel_bit(0)  # isense_input_sel ; 0 for high

    apc_reg.set_pa_hb_gain_en_dr(1)  # pa_hb_gain_en  10
    apc_reg.set_pa_hb_gain_en_reg(0)  # pa_hb_gain_en  10

    cal_ipa_vofst = volt_ms_robust_avg(msadc0, 3)
    print(f'offset_volt:  {cal_ipa_vofst}')

    apc_reg.set_pa_hb_gain_en_reg(1)

    cur_now = (volt_ms_robust_avg(msadc0, 3) - cal_ipa_vofst) / res_hb

    print(f'电流：{cur_now}')

    apc_reg.release_apc_high_table_gain()
    apc_reg.set_wf_pa_isense_en(0)  # isense_en    isense_rbit
    apc_reg.set_wf_test_enable_pa(0)

    msadc0.testmux(0, 0)  # test mode ,bit
    apc_reg.set_pa_hb_gain_en_dr(0)  # pa_hb_gain_en  00
    apc_reg.set_pa_hb_gain_en_reg(0)

    apc_reg.set_wf_pu_dtmx_wf_hb_dr(0)
    apc_reg.set_wf_pu_dtmx_wf_hb_reg(0)

    UARTc.sendcmd('tone_off')
    # uart_close()

    # return incre, cur_final
    return cur_now



def cal_ipa_lb():
    UARTc = uart_open(3)
    res_lb = 1.12

    UARTc.sendcmd('setch 7')
    time.sleep(2)
    UARTc.sendcmd('tone_off')

    UARTc.sendcmd('tone_on 0 0 9')
    time.sleep(0.5)

    # UARTc.sendcmd('tc 0')

    apc_reg = ApcReg(UARTc)
    msadc0 = MSADC(clk_div=40, acc_mode=1)
    msadc0.ms_portdc_config()

    # apc_reg.fix_apc_low_table_gain()  # high rate table , fix c

    apc_reg.set_wf_pu_dtmx_wf_lb_dr(1)
    apc_reg.set_wf_pu_dtmx_wf_lb_reg(0)  #

    apc_reg.set_wf_test_enable_pa(1)

    apc_reg.set_wf_pa_isense_en(1)  # isense_en    isense_rbit
    msadc0.testmux(3, 0)  # test mode ,bit
    # msadc0.portdc_mode(2)
    # msadc0.portdc_bit(6)

    apc_reg.set_wf_isense_input_sel_bit(1)  # isense_input_sel ; 0 for high

    apc_reg.set_pa_lb_gain_en_dr(1)  # pa_hb_gain_en  10
    apc_reg.set_pa_lb_gain_en_reg(0)  # pa_hb_gain_en  10

    cal_ipa_vofst = volt_ms_robust_avg(msadc0, 3)
    print(f'offset_volt:  {cal_ipa_vofst}')

    apc_reg.set_pa_lb_gain_en_reg(1)

    cur_now = (volt_ms_robust_avg(msadc0, 3) - cal_ipa_vofst) / res_lb

    print(f'电流：{cur_now}')

    apc_reg.release_apc_low_table_gain()
    apc_reg.set_wf_pa_isense_en(0)  # isense_en    isense_rbit
    apc_reg.set_wf_test_enable_pa(0)

    msadc0.testmux(0, 0)  # test mode ,bit
    apc_reg.set_pa_lb_gain_en_dr(0)  # pa_hb_gain_en  00
    apc_reg.set_pa_lb_gain_en_reg(0)

    apc_reg.set_wf_pu_dtmx_wf_lb_dr(0)
    apc_reg.set_wf_pu_dtmx_wf_lb_reg(0)

    UARTc.sendcmd('tone_off')
    uart_close()

    return cur_now




if __name__ == "__main__":

    temp = 25

    # # incre, cur_final = cal_ipa_lb()
    # cur_5g = cal_ipa_hb()
    # cur_2g4 = cal_ipa_lb()
    # print(cur_5g, cur_5g)
    # # cal_ipa_lb()

    cur_file = r'.\data\Aic8819_data_Temp_Cur.xlsx'
    cur_dict = {}

    cur_5g = cal_ipa_hb()
    cur_2g4 = cal_ipa_lb()
    print(f"--------cur: ")
    # print_red(cur_5g)

    cur_dict['Temp'] = temp
    cur_dict['Curr2G4'] = round(cur_2g4, 2)
    cur_dict['Curr5G'] = round(cur_5g, 2)

    print("row:", cur_dict)
    save_results(cur_dict, cur_file)