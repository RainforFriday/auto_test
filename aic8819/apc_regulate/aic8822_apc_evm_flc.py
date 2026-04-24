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
from toolkit.ApcReg import *
from toolkit.util import *

def other():
    # measure pwr and evm
    if wlan_standard == "11b":
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


def get_ms_res():
    CMPX.wlan_Adjust_lvl()
    CMPX.wlan_meas_start()
    time.sleep(1)

    res = CMPX.wlan_meas_avg()
    ms_pwr = res.split(",")[12]
    ms_evm_avg = res.split(",")[15]
    CMPX.wlan_meas_abort()
    return ms_pwr, ms_evm_avg

def swp_apc(reg_name,high,low):
    # data_dict['reg_name'] = "vh_vm_ref"
    data_dict['reg_name'] = reg_name
    # high = 63
    # low = 60
    n = high - low + 1
    default = apc_reg.get_8822_rapc_common_bit(addrs, high, low)
    list = range(2 ** n // 3, (2 * 2 ** n) // 3, 1)
    if n > 4:
        list = range(2 ** n // 3, (2 * 2 ** n) // 3, 2)
    for k in list:
        # apc_reg.set_8822_wapc_common_bit(addrs, high, low, k)
        data_dict['reg_val'] = k
        pwr_list = []
        evm_list = []
        for count in range(5):
            UARTX.sendcmd("settx 0")
            UARTX.sendcmd("calib 3 80002000 2 5500 0")
            time.sleep(1)
            UARTX.sendcmd("settx 1")
            ms_res = get_ms_res()
            pwr_list.append(round(float(ms_res[0]), 2))
            evm_list.append(round(float(ms_res[1]), 2))

        for j in range(5):
            data_dict[f'pwr{j + 1}'] = pwr_list[j]
        data_dict[f'pwr_range'] = round(max(pwr_list) - min(pwr_list), 2)
        for j in range(5):
            data_dict[f'evm{j + 1}'] = evm_list[j]
        data_dict[f'evm_range'] = round(max(evm_list) - min(evm_list), 2)

        print("保存的数据行：", data_dict)
        save_results(data_dict, file_path)

    apc_reg.set_8822_wapc_common_bit(addrs, high, low, default)

if __name__ == "__main__":

    # Agilent = agilent(5)
    # Agilent.open()

    # Agilent.OUTP_OFF()
    # Agilent.Cur_Mode()
    # Agilent.set_Chl1(3.3, 3)
    # Agilent.curtrange()
    # Agilent.OUTP_ON()
    # time.sleep(0.1)

    xlsx_path = r'.\Table\TABLE_apc_evm_flc.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file_path = r'.\data\8822_apc_evm_flc_data_'+current_time+'.xlsx'
    # file_path = r'.\data\8822_apc_evm_flc_data_1.xlsx'
    data_dict = {}

    UARTX = Uart(19, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()
    apc_reg = ApcReg(UARTX, is22=1)


    bin_file = "8822_svn2_1023.bin"
    # bin_file = "testmode_8822_924_6e_temp.bin"

    # # once
    # UARTX.sendcmd('reboot')
    # time.sleep(2)
    bin_file_path = './bin/'+bin_file
    load_bin_X16(UARTX, bin_file_path)

    address = "TCPIP0::10.21.10.200::hislip0::INSTR"
    CMPX = CMP180vs(address)

    apc_reg.release_8822_apc_ant0_tx_gain_reg()

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
        # UARTX.sendcmd("pwrmm 1")
        # UARTX.sendcmd("tc 0")
        UARTX.sendcmd("pwrofst2x 3 0 2 1")
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
            # UARTX.sendcmd(setchx)

            for setpwrx in db_line.l_setpwr_ucmd():
                setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                # UARTX.sendcmd(setpwrx)
                UARTX.sendcmd("pwrlvl 2 1 9 15")

                UARTX.sendcmd("settx 0")
                UARTX.sendcmd(f"setch {ch}")
                time.sleep(2)
                UARTX.sendcmd("settx 1")

                time.sleep(0.2)

                cmdx = ""
                # print(db_line.l_uartcmd())
                try:
                    if db_line.l_uartcmd() is not None:
                        for u_cmdx in db_line.l_uartcmd():
                            cmdx = cmdx + UARTX.sendcmd(u_cmdx)
                            # print(cmdx)
                except:
                    cmdx = "ERROR"

                for key_str in [",", "\n", "\r", "aic>"]:
                    cmdx = cmdx.replace(key_str, " ")

                analog_char = get_analog_gear(UARTX)
                analog = int(analog_char, 16)

                fix_table = 1
                fix_table_gain = (fix_table << 4) | analog
                # apc_reg.fix_8822_apc_ant0_tx_gain_reg(fix_table_gain)
                # assert fix_table == rate_group_lst[index] + ch_group_lst[
                #     index] * 3, f"fix_table unright, index{index}: {fix_table}"

                addrs = get_8822_apc_addr(1, analog)
                # addr_low = addrs[0]


                data_dict['OK'] = db_line.boardno()
                data_dict['ANT'] = db_line.ant()
                data_dict['bin'] = bin_file
                data_dict['ch'] = ch
                data_dict['rate'] = rate
                data_dict['bw'] = bw
                data_dict['len'] = len
                data_dict['setpwr'] = setpwr
                data_dict['cmdx'] = cmdx

                swp_apc("no", 63, 60)

                # swp_apc("pa_vm_ref_bit", 63, 60)
                # swp_apc("pa_vh_vbit", 59, 57)
                # swp_apc("padrv_vl_iv_it", 41, 36)
                # swp_apc("tmx_vlo_vbit", 20, 18)
                # swp_apc("vl_ib_bit", 9, 5)
                # swp_apc("vl_it_bit", 4, 0)

            # apc_reg.release_8822_apc_ant0_tx_gain_reg()
            UARTX.sendcmd("settx 0")
    UARTX.close()
    # Agilent.OUTP_OFF()


    # data_dict[f'pwr_{count}'] = ms_res[0]
    # data_dict[f'evm_{count}'] = ms_res[1]
    #
    # try:
    #     data_dict[f'pwr_{count}'] = round(float(ms_res[0]), 2)
    # except ValueError:
    #     data_dict[f'pwr_{count}'] = ms_res[0]
    #
    # try:
    #     data_dict[f'evm_{count}'] = round(float(ms_res[1]), 2)
    # except ValueError:
    #     data_dict[f'evm_{count}'] = ms_res[1]





