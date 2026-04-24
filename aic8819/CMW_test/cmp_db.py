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


if __name__ == "__main__":

    # Agilent = agilent(5)
    # Agilent.open()

    # Agilent.OUTP_OFF()
    # Agilent.Cur_Mode()
    # Agilent.set_Chl1(3.3, 3)
    # Agilent.curtrange()
    # Agilent.OUTP_ON()
    # time.sleep(0.1)

    xlsx_path = r'.\Table\cmp_TABLE_pwr.xlsx'
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    file_path = r'.\data\cmp_8819_data_'+current_time+'.xlsx'
    data_dict = {}

    UARTX = Uart(3, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    bin_file = "testmode19_2025_1113_2037.bin"
    # bin_file = "testmode_8822_924_6e_temp.bin"

    # # once
    # UARTX.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = './bin/'+bin_file
    # load_bin_X10(UARTX, bin_file_path)
    # time.sleep(1)


    # address = "TCPIP0::10.21.12.195::hislip0::INSTR"
    address = "TCPIP0::192.168.1.102::hislip0::INSTR"
    CMPX = CMP180vs(address)

    UARTX.sendcmd("setxtalcap 2")
    UARTX.sendcmd("settx 0")
    UARTX.sendcmd("pwrmm 1")

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
            for setpwrx in db_line.l_setpwr_ucmd():
                setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                UARTX.sendcmd(setpwrx)

                UARTX.sendcmd("settx 1")
                time.sleep(0.2)

                cmdx = ""
                # print(db_line.l_uartcmd())
                try:
                    if db_line.l_uartcmd() is not None:
                        for u_cmdx in db_line.l_uartcmd():
                            # cmdx = cmdx + UARTX.sendcmd(u_cmdx)
                            cc2 = UARTX.sendcmd(u_cmdx)
                            cmdx = cc2.split('\n')[1].strip()

                            # print(cmdx)
                except:
                    cmdx = "ERROR"

                for key_str in [",", "\n", "\r", "aic>"]:
                    cmdx = cmdx.replace(key_str, " ")

                CMPX.wlan_Adjust_lvl()
                CMPX.wlan_meas_start()
                time.sleep(1)

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
                iqofst = CMPX.wlan_meas_IQoffset()
                dc_pwr = CMPX.wlan_meas_DCPwr()

                data_dict['OK'] = db_line.boardno()
                # data_dict['ANT'] = db_line.ant()
                data_dict['bin'] = bin_file
                data_dict['ch'] = ch
                data_dict['rate'] = rate
                data_dict['bw'] = bw
                data_dict['len'] = len
                data_dict['setpwr'] = setpwr
                data_dict['cmdx'] = cmdx
                data_dict['pwr'] = ms_pwr
                # data_dict['peak_pwr'] = str(peak_pwr)

                data_dict['evm'] = ms_evm_avg
                data_dict['evm_peak'] = ms_evm_peak
                data_dict['mask_avg'] = ms_mask_avg
                data_dict['mask_max'] = ms_mask_max


                data_dict['clock'] = clock
                data_dict['IQofst'] = iqofst
                data_dict['DC Pwr'] = dc_pwr

                print("保存的数据行：", data_dict)
                save_results(data_dict, file_path)

            UARTX.sendcmd("settx 0")
    CMPX.wlan_meas_abort()
    UARTX.close()
    # Agilent.OUTP_OFF()






