from aicintf.uart import *
from aicintf.agilent import *
from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
import pyvisa as visa
# from aicintf.gpib import *
import time
import csv
import datetime
# from aic8819.PXA import *
from MsPFM.ms_wf import *
# from icbasic.aicinstr.rs.cmp180 import *
# from icbasic.aicintf.uart import *
from icbasic.toolkit.CMP180vs import *
from icbasic.toolkit.util import *
from MsPFM.msadc import *
from toolkit.ApcReg import *
import re

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

    temp = 100

    # xlsx_path = r'.\Table\cmp_TABLE_pwr.xlsx'
    # xlsx_path = r'.\Table\cmp_TABLE_sample.xlsx'
    xlsx_path = r'.\Table\cmp_TABLE_temp.xlsx'

    start_time = time.time()

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    # file_path = r'.\data\cmp_8819_data_'+current_time+'.xlsx'
    file_path = r'.\data\cmp_8819_data_Temp_flow_verify.xlsx'
    data_dict = {}

    UARTX = Uart(3, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()


    bin_file = "testmode19_dbg_temp_0112.bin"
    # bin_file = "testmode19_2026_0106_1559_g3370547-20260106.bin"
    # bin_file = "testmode_8822_924_6e_temp.bin"

    # # once
    # UARTX.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = './bin/'+bin_file
    # load_bin_X10(UARTX, bin_file_path)
    # time.sleep(1)


    address = "TCPIP0::10.21.12.199::hislip0::INSTR"
    CMPX = CMP180vs(address)

    UARTX.sendcmd("settx 0")
    # UARTX.sendcmd("tc 0")

    # UARTX.sendcmd("pwrmm 1")
    # UARTX.sendcmd("setintv 2000")

    table_lines = WF_MS_TABLE(xlsx_path).read()
    for linex in table_lines:
        db_line = WF_MS_LINE(linex)
        if db_line.enable() not in ["Y", "y", "YES", "yes"]:
            continue
        # print(db_line.l_setch_ucmd())
        # print(db_line.l_setpwr_ucmd())
        # print(db_line.setbw_ucmd())
        # print(db_line.setrate_ucmd())
        # UARTX.sendcmd("settx 1")
        UARTX.sendcmd(db_line.setrate_ucmd())
        UARTX.sendcmd(db_line.setbw_ucmd())
        UARTX.sendcmd(db_line.setlen_ucmd())
        rate = " ".join(db_line.setrate_ucmd().strip().split(" ")[1:])
        bw = " ".join(db_line.setbw_ucmd().strip().split(" ")[1:])
        len = " ".join(db_line.setlen_ucmd().strip().split(" ")[1:])

        # set route
        if db_line.route() != "":
            CMPX.wlan_set_route(db_line.route())

        wlan_standard = get_wlan_stand_by_rate(rate)
        CMPX.wlan_set_standard(wlan_standard)

        # print(bw)
        if "0 0" in bw:
            CMPX.wlan_set_bandwidth("20")
        elif "1 1" in bw:
            CMPX.wlan_set_bandwidth("40")
        elif "2 2" in bw:
            CMPX.wlan_set_bandwidth("80")

        for setchx in db_line.l_setch_ucmd():
            ch = setchx.strip().split(" ")[1]
            CMPX.wlan_set_freq_by_ch(ch)
            UARTX.sendcmd(setchx)
            # UARTX.sendcmd(f"setch {ch}")

            time.sleep(2)

            # dpd_flag = 1

            for setpwrx in db_line.l_setpwr_ucmd():
                # setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                # UARTX.sendcmd(setpwrx)

                # # pll cal
                # UARTX.sendcmd("w 4034184 1")
                # time.sleep(0.2)

                UARTX.sendcmd("settx 1")
                time.sleep(0.2)

                ret = UARTX.sendcmd('t')
                # match = re.search(r'Temp\s*:\s*(\d+)\s*C', ret)
                match = re.search(r'Temp\s*:\s*(-?\d+)\s*C', ret)
                if match:
                    chip_temp = match.group(1)

                    print(f"t={chip_temp} C")

                max_retries = 3
                for attempt in range(max_retries):
                    CMPX.wlan_Adjust_lvl()
                    CMPX.wlan_meas_start()
                    time.sleep(0.5)

                    # res = CMPX.wlan_meas_avg()
                    # ms_pwr = res.split(",")[12]
                    # ms_evm_avg = res.split(",")[15]

                    clock = CMPX.wlan_meas_clock_error()

                    # measure pwr and evm
                    if wlan_standard == "11b":
                        clock = CMPX.wlan_meas_11b_clock_error()

                        if db_line.res_pwr():
                            ms_pwr = CMPX.wlan_meas_11b_pwr()
                        else:
                            ms_pwr = "NA"
                        if db_line.res_evm_avg():
                            ms_evm_avg = CMPX.wlan_meas_11b_evm_rms()
                        else:
                            ms_evm_avg = "NA"
                        if db_line.res_evm_peak():
                            ms_evm_peak = CMPX.wlan_meas_11b_evm_peak()
                        else:
                            ms_evm_peak = "NA"
                    else:
                        if db_line.res_pwr():
                            ms_pwr = CMPX.wlan_meas_pwr()
                        else:
                            ms_pwr = "NA"
                        if db_line.res_evm_avg():
                            ms_evm_avg = CMPX.wlan_meas_evm()
                        else:
                            ms_evm_avg = "NA"
                        if db_line.res_evm_peak():
                            ms_evm_peak = CMPX.wlan_meas_evm_peak()
                        else:
                            ms_evm_peak = "NA"

                    # measure mask
                    if db_line.res_mask_avg():
                        ms_mask_avg = CMPX.wlan_meas_tsmask_avg_maxval()
                    else:
                        ms_mask_avg = "NA"

                    if db_line.res_mask_max():
                        ms_mask_max = CMPX.wlan_meas_tsmask_max_maxval()
                    else:
                        ms_mask_max = "NA"

                    # peak_pwr = CMPX.wlan_meas_peak_pwr()
                    # clock = CMPX.wlan_meas_clock_error()
                    # iqofst = CMPX.wlan_meas_IQoffset()
                    # dc_pwr = CMPX.wlan_meas_DCPwr()


                    if float(ms_pwr) > -20.0:
                        break
                    print_red(f"failed, again!")
                    UARTX.sendcmd(setchx)
                    time.sleep(1.5)
                    CMPX.wlan_meas_abort()
                    # UARTX.sendcmd(setpwrx)
                    UARTX.sendcmd("settx 1")

                evm_limit = get_evm_limit_by_rate(rate)

                evm_pass = 'y' if float(ms_evm_avg) < evm_limit else 'n'
                mask_pass = 'y' if float(ms_mask_max) < 0 else 'n'



                data_dict['OK'] = db_line.boardno()
                # data_dict['ANT'] = db_line.ant()
                data_dict['bin'] = bin_file
                data_dict['ch'] = ch
                data_dict['rate'] = rate
                data_dict['bw'] = bw
                # data_dict['len'] = len
                # data_dict['cmdx'] = cmdx
                # data_dict['setpwr'] = setpwr

                data_dict['temp'] = temp
                data_dict['chip_temp'] = chip_temp
                data_dict['pwr'] = ms_pwr
                # data_dict['peak_pwr'] = str(peak_pwr)

                data_dict['evm'] = ms_evm_avg
                data_dict['clock'] = clock

                data_dict["evm_limit"] = evm_limit
                data_dict['evm_pass'] = evm_pass
                # data_dict['evm_peak'] = ms_evm_peak
                # data_dict['mask_avg'] = ms_mask_avg
                data_dict['mask_avg'] = round(float(ms_mask_avg), 2)
                data_dict['mask_max'] = round(float(ms_mask_max), 2)
                data_dict["mask_pass"] = mask_pass

                # data_dict['IQofst'] = iqofst
                # data_dict['DC Pwr'] = dc_pwr

                print("row:", data_dict)
                save_results(data_dict, file_path)

            UARTX.sendcmd("settx 0")
    CMPX.wlan_meas_abort()
    UARTX.close()




    # UARTX.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"执行时间: {elapsed_time/60 :.2f} min")

    # Agilent.OUTP_OFF()





