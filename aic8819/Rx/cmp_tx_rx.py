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
from aic8819.Rx.cmp_rx import *
# Agilent = agilent(5)
    # Agilent.open()

    # Agilent.OUTP_OFF()
    # Agilent.Cur_Mode()
    # Agilent.set_Chl1(3.3, 3)
    # Agilent.curtrange()
    # Agilent.OUTP_ON()
    # time.sleep(0.1)

def repeat_ms():
    UARTX.sendcmd(setchx)
    time.sleep(1.5)
    CMPX.wlan_meas_abort()
    UARTX.sendcmd(setpwrx)

    UARTX.sendcmd("settx 1")
    # time.sleep(0.2)

    # CMPX.wlan_set_peakpwr(30)
    CMPX.wlan_Adjust_lvl()
    CMPX.wlan_meas_start()

    time.sleep(0.5)

    # res = CMPX.wlan_meas_avg()
    # ms_pwr = res.split(",")[12]
    # ms_evm_avg = res.split(",")[15]

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

    return ms_pwr, ms_evm_avg


if __name__ == "__main__":

    NO = 150
    # NO = 94
    xlsx_path = r'.\Table\cmp_TABLE_pwr.xlsx'
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    passtx = 0
    passbin = 0

    file_path = r'.\data\cmp_8819D80EN2_data_tx.xlsx'
    data_dict = {}
    loss = 1.5


    # 记录开始时间
    start_time = time.time()

    UARTX = Uart(3, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    # bin_file = "testmode19_2025_1107_2131.bin"
    bin_file = "testmode19_2025_1113_2037.bin"

    if not passbin:
        # # once
        # UARTX.sendcmd('reboot')
        # time.sleep(2)
        bin_file_path = './bin/'+bin_file
        load_bin_X10(UARTX, bin_file_path)
        time.sleep(0.5)


    # address = "TCPIP0::10.21.12.184::hislip0::INSTR"
    address = "TCPIP0::192.168.1.102::hislip0::INSTR"
    CMPX = CMP180vs(address)

    # UARTX.sendcmd(f"setxtalcap 2")
    UARTX.sendcmd("pwrmm 1")

    # CMPX.wlan_set_peakpwr(30)
    # CMPX.sa.write("CONFigure:WLAN:MEAS:MEValuation:SCOunt:MODulation 5")

    if not passtx:

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

                time.sleep(1.5)
                for setpwrx in db_line.l_setpwr_ucmd():
                    setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                    UARTX.sendcmd(setpwrx)

                    UARTX.sendcmd("settx 1")
                    # time.sleep(0.2)

                    # CMPX.wlan_set_peakpwr(30)
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

                    # CMPX.wlan_meas_abort()
                    CMPX.wlan_meas_stop()

                    if int(ch) > 7:
                        ms_pwr = float(ms_pwr) + loss
                        if float(ms_pwr) < -20.0:
                            print_red("again!")
                            ms_pwr, ms_evm_avg = repeat_ms()
                            ms_pwr = float(ms_pwr) + loss
                            if float(ms_pwr) < -20.0:
                                print_red("again!")
                                ms_pwr, ms_evm_avg = repeat_ms()
                                ms_pwr = float(ms_pwr) + loss
                                if float(ms_pwr) < -20.0:
                                    print_red("again!")
                                    ms_pwr, ms_evm_avg = repeat_ms()
                                    ms_pwr = float(ms_pwr) + loss
                    elif float(ms_pwr) < -20.0:
                            print_red("again!")
                            ms_pwr, ms_evm_avg = repeat_ms()
                            if float(ms_pwr) < -20.0:
                                print_red("again!")
                                ms_pwr, ms_evm_avg = repeat_ms()
                                if float(ms_pwr) < -20.0:
                                    print_red("again!")
                                    ms_pwr, ms_evm_avg = repeat_ms()


                    data_dict['No'] = NO
                    # data_dict['ANT'] = db_line.ant()
                    data_dict['bin'] = bin_file
                    data_dict['ch'] = ch
                    data_dict['rate'] = rate
                    data_dict['bw'] = bw
                    # data_dict['len'] = len
                    data_dict['setpwr'] = setpwr
                    # data_dict['cmdx'] = cmdx
                    data_dict['pwr'] = ms_pwr
                    # data_dict['peak_pwr'] = str(peak_pwr)

                    data_dict['evm'] = ms_evm_avg
                    # data_dict['evm_peak'] = ms_evm_peak
                    data_dict['mask_avg'] = ms_mask_avg
                    data_dict['mask_max'] = ms_mask_max

                    data_dict['clock_error'] = clock

                    print(data_dict)
                    save_results(data_dict, file_path)

                UARTX.sendcmd("settx 0")

    CMPX.wlan_meas_abort()

    # 计算用时
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"{elapsed_time:.3f} s")
    print("------")


    #RX
    # rxfile_path = r'.\data\cmp_8819D80EN2_data_rx补测.xlsx'
    rxfile_path = r'.\data\cmp_8819D80EN2_data_rx.xlsx'
    rx_dict = {}


    # rx
    # for ch in [7, 42]:
    for ch in [42]:
        UARTX.sendcmd(f"setch {ch}")
        time.sleep(1.5)
        if ch == 7:
            CMPX.sge_set_route("RF1.1")
        else:
            CMPX.sge_set_route("RF1.8")
        # for bw in [20, 40]:
        for bw in [40]:
            # if ch == 7 and bw == 80:
            #     continue

            if bw == 20:
                UARTX.sendcmd(f"setbw 0 0")
            elif bw == 40:
                UARTX.sendcmd(f"setbw 1 1")
            elif bw == 80:
                UARTX.sendcmd(f"setbw 2 2")

            # for mcs in [0, 11]:
            for mcs in [11]:
                # if bw == 80 and mcs == 11:
                #     continue

                if mcs == 0:
                    wait_time = 2
                    if ch == 7:
                        pmin = -88
                        pmax = -70
                        # pmax = -79
                        if bw == 40:
                            pmin = -92
                            pmax = -81
                    else:
                        # 42 0
                        pmin = -95
                        pmax = -86
                        if bw == 40:
                            pmin = -93
                            pmax = -86
                elif mcs == 11:
                    wait_time = 1.2
                    if ch == 7:
                        pmin = -70
                        pmax = -58
                        if bw == 40:
                            pmin = -68
                            pmax = -55
                    else:
                        # 42 11
                        pmin = -70
                        pmax = -55
                        if bw == 40:
                            pmin = -68
                            # pmax = -42
                            pmax = -55


                    # pmin = -70
                    # pmax = -30

                rate = "11ax"
                # bw = 20
                # mcs = 7
                # UARTX.sendcmd("settx 0")

                freq = get_freq_by_ch(ch)
                CMPX.sge_arb_set_cfreq(freq)
                CMPX.sge_arb_rep(mode="SINGle")
                CMPX.sge_arb_rep_count()
                ## CMPX.sge_arb_on()
                CMPX.sge_arb_list_incre(mode="ACYCles")
                wave = f"11ax_{bw}M_mcs{mcs}_1024.wv"

                CMPX.sge_arb_set_wave(wave)
                opt_pwr, per = find_optimal_power(UARTX, CMPX, measure_per, p_min=pmin, p_max=pmax, target=10,
                                                  tol=0.7, wait=wait_time)
                # print(f'choose pwr: {opt_pwr}   per : {per}')

                CMPX.sge_arb_off()
                UARTX.sendcmd("statrxstop")

                rx_dict['NO'] = NO
                rx_dict['ch'] = ch
                rx_dict['rate'] = rate
                rx_dict['mcs'] = mcs
                rx_dict['bw'] = bw
                rx_dict['lvl'] = opt_pwr
                rx_dict['per'] = per

                print(rx_dict)
                save_results(rx_dict, rxfile_path)

    # 计算用时
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"{elapsed_time:.3f} s")
    print("------")


    UARTX.close()
    # Agilent.OUTP_OFF()

    # cmdx = ""
    # # print(db_line.l_uartcmd())
    # try:
    #     if db_line.l_uartcmd() is not None:
    #         for u_cmdx in db_line.l_uartcmd():
    #             # cmdx = cmdx + UARTX.sendcmd(u_cmdx)
    #             cc2 = UARTX.sendcmd(u_cmdx)
    #             cmdx = cc2.split('\n')[1].strip()
    #
    #             # print(cmdx)
    # except:
    #     cmdx = "ERROR"
    #
    # for key_str in [",", "\n", "\r", "aic>"]:
    #     cmdx = cmdx.replace(key_str, " ")





