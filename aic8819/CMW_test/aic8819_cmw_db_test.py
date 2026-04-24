# from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
# from aicintf.gpib import *
from MsPFM.ms_wf import *

from RsCmwWlanMeas import *
import sys
# from datetime import datetime
sys.path.append("../lib/")
from aic8819.CMW_test.lib import device
# import TX.Jupyter.lib.device

from icbasic.toolkit.util import *


def tuner_init(tuner1,UART1,freq):
    tuner1.open(UART1)
    tuner1.init_tune(UART1)
    time.sleep(2)
    tuner1.load_file(UART1, str(freq))
    time.sleep(2)

def load_bin(UART2,bin_file_path):
    UART2.xmodem_load_bin("x 160000", bin_file_path)
    xxx = UART2.sendcmd("g 160000")
    print(xxx)

def fsq_init(fsqx):
    fsqx.set_analyzer_mode()
    # fsqx.set_span(100)

    fsqx.set_rb(1)
    fsqx.set_vb(3)
    fsqx.set_reflvl(30)
    # fsqx.set_cfreq(freq)
    time.sleep(0.5)

def meas_fsq(pxa):
    # tt = pxa.get_peak_mark()
    tt = pxa.get_peak_mark_until_idle()
    mark_pwr = str(round(float(tt[1]), 2))
    mark_freq = str(round(float(tt[0]) / 1000000, 2))
    return mark_pwr, mark_freq

def set_auto_ref_pwr(fsqx):
    # self.set_reflvl(30)
    time.sleep(1)
    pwr = fsqx.get_peak_mark()[1]
    if int(float(pwr))<30:
        fsqx.set_reflvl(int(float(pwr)) + 15)
        time.sleep(1)

def set_band(pxa,start,stop,loss):
    # pxa.set_reflvl(30)
    pxa.set_startfreq(start)
    pxa.set_stopfreq(stop)
    # pxa.set_auto_ref_pwr()
    pwr, freq = meas_fsq(pxa)
    pwr = round(float(pwr)+loss, 2)
    return str(pwr),freq

def mea_muti_band(pxa,freq,loss):
    # fsq_init(fsqx, 200, 2400)
    pxa.sa.write("*CLS")
    pwr02,freq02=set_band(pxa,0.03, freq-40,loss)
    pwr24,freq24=set_band(pxa,freq-40, freq+40,loss)
    pwr25,freq25=set_band(pxa,freq+40,  2*freq-80,loss)
    pwr48,freq48=set_band(pxa,2*freq-80, 2*freq+80,loss)
    pwr50,freq50=set_band(pxa,2*freq+80, 3*freq-120,loss)
    pwr72,freq72=set_band(pxa,3*freq-120, 3*freq+120,loss)
    pwr75,freq75=set_band(pxa,3*freq+120, 26000,loss)
    return pwr02,freq02,pwr24,freq24,pwr25,freq25,pwr48,freq48,\
           pwr50,freq50,pwr72,freq72,pwr75,freq75

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
            ResultData = driver.multiEval.modulation.average.fetch()
            # device.wait_ms(500)
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
                device.wait_ms(4000)

        # 如果执行完 max_try 次仍未成功，返回最后的 clk_err
        print("❌ 失败：多次尝试后仍未成功")
        return clk_err
    except Exception as e:
        clk_err = float('nan')
    return clk_err




if __name__ == "__main__":

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_all_sample.xlsx'
    xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_5G_MaxPwr.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\Tuner_swp_data_20250805.csv'
    file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\data\cmw_data_'+current_time+'.xlsx'

    RsCmwWlanMeas.assert_minimum_version('3.8.20')
    # instr_list = RsCmwWlanMeas.list_resources("?*")
    # print(instr_list)
    # resource_string_1 = 'TCPIP0::10.21.10.124::INSTR'  # Standard LAN connection (also called VXI-11)
    # resource_string_1 = 'TCPIP0::CMW50050-170904::inst1'  # Standard LAN connection (also called VXI-11)
    resource_string_1 = 'TCPIP0::10.21.10.124::hislip0'  # Standard LAN connection (also called VXI-11)
    # Initializing the session
    driver = RsCmwWlanMeas(resource_string_1)
    idn = driver.utilities.query_str('*IDN?')
    print(f"\nHello, I am: '{idn}'")
    # print(f'RsCmwWlanMeas package version: {driver.utilities.driver_version}')
    # print(f'Visa manufacturer: {driver.utilities.visa_manufacturer}')
    # print(f'Instrument full name: {driver.utilities.full_instrument_model_name}')
    # print(f'Instrument installed options: {",".join(driver.utilities.instrument_options)}')


    # UARTX = Uart(8, wr_mode=True)
    # UARTX.set_baudrate("921600")
    # UARTX.open()
    # bb1=UARTX.sendcmd('r 403422c8').split('\r')[1].strip()
    # print(bb1)

    data_pool_8819 = {'utm_bin': r"D:\Aic8800\Code\rf_test\UTM\TX\Pycharm\bin\testmode_8819h_820_high_apc.bin",
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
    dut = device.dut(data_pool_8819, 'COM8')
    # once
    # prt_out = dut.load_bin()
    # for x in prt_out:
    #     print(x)




    data_dict = {}

    # cc2 = dut.uart.send("r 403422c8")
    # cmdx = cc2[0].split('\n')[2].strip()
    #
    # print(dut.uart.send("r 403422c8"))


    dut.uart.send("pwrmm 1")
    dut.uart.send("setintv 500")

    table_lines = WF_MS_TABLE(xlsx_path).read()
    with tqdm(total=(len(table_lines))) as pbar:
        for linex in table_lines:
            db_line = WF_MS_LINE(linex)
            if db_line.enable() not in ["Y", "y", "YES", "yes"]:
                continue

            dut.uart.send(db_line.setrate_ucmd())
            dut.uart.send(db_line.setbw_ucmd())
            dut.uart.send(db_line.setlen_ucmd())
            rate = " ".join(db_line.setrate_ucmd().strip().split(" ")[1:])
            bw = " ".join(db_line.setbw_ucmd().strip().split(" ")[1:])
            len_set = " ".join(db_line.setlen_ucmd().strip().split(" ")[1:])

            pbar.update(1)
            print(pbar)

            wlan_standard = "11ax"
            if rate.strip().split(" ")[0] == "5":
                wlan_standard = "11ax"
            elif rate.strip().split(" ")[0] == "4":
                wlan_standard = "11ac"
            elif rate.strip().split(" ")[0] == "2":
                wlan_standard = "11n"
            elif rate.strip().split(" ")[0] == "0":
                if rate.strip().split(" ")[1] in ["0", "1", "2", "3"]:
                    wlan_standard = "11b"
                else:
                    wlan_standard = "11g"

            driver.configure.rfSettings.eattenuation.set(10, connector=repcap.Connector.Default)


            # config std bw
            if wlan_standard == '11b':
                driver.configure.isignal.set_standard(enums.IeeeStandard.DSSS)
            elif wlan_standard == '11g':
                driver.configure.isignal.set_standard(enums.IeeeStandard.LOFDm)
            elif wlan_standard == '11n':
                driver.configure.isignal.set_standard(enums.IeeeStandard.HTOFdm)
            elif wlan_standard == '11ac':
                driver.configure.isignal.set_standard(enums.IeeeStandard.VHTofdm)
            else:
                driver.configure.isignal.set_standard(enums.IeeeStandard.HEOFdm)

            if "0 0" in bw:
                driver.configure.isignal.set_bandwidth(bandwidth=enums.Bandwidth.BW20mhz)
            elif "1 1" in bw:
                driver.configure.isignal.set_bandwidth(bandwidth=enums.Bandwidth.BW40mhz)
            else:
                driver.configure.isignal.set_bandwidth(bandwidth=enums.Bandwidth.BW80mhz)

            for setchx in db_line.l_setch_ucmd():
                ch = setchx.strip().split(" ")[1]
                freq = get_freq_by_ch(ch)
                dut.uart.send(setchx)
                time.sleep(1.2)

                # if ch > 35:
                #     channel = (5180 + (ch - 36) * 5) * 1000000.0
                # else:
                #     channel = (2412 + (ch - 1) * 5) * 1000000.0
                # device.wait_ms(10)
                driver.configure.rfSettings.frequency.set_value(frequency=freq*1e6)
                device.wait_ms(50)


                for setpwrx in db_line.l_setpwr_ucmd():
                    start_time = time.time()

                    setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                    setpwr = int(setpwr)
                    dut.uart.send(setpwrx)
                    dut.uart.send("settx 1")

                    cmdx = ""
                    # print(db_line.l_uartcmd())
                    try:
                        if db_line.l_uartcmd() is not None:
                            for u_cmdx in db_line.l_uartcmd():
                                # cmdx = cmdx + dut.uart.send(u_cmdx)
                                cc2 = dut.uart.send(u_cmdx)
                                cmdx = cc2[0].split('\n')[2].strip()
                                # print(cmdx)
                    except:
                        cmdx = "ERROR"

                    for key_str in [",", "\n", "\r", "aic>"]:
                        cmdx = cmdx.replace(key_str, " ")

                    time.sleep(0.2)

                    # config exp
                    if wlan_standard == '11b':
                        if setpwr < 2:
                            exp_pwr_con = 2 + 7
                        else:
                            exp_pwr_con = setpwr + 7
                    else:
                        if setpwr < -8:
                            exp_pwr_con = -8 + 12
                        else:
                            exp_pwr_con = setpwr + 15
                    # set expected power
                    driver.configure.rfSettings.envelopePower.set(exp_pwr_con, connector=repcap.Connector.Default)

                    # device.wait_ms(100) upadte
                    driver.multiEval.stop()
                    driver.multiEval.initiate()
                    device.wait_ms(3000)

                    # Clock_Error
                    # ResultData = driver.multiEval.modulation.average.fetch()
                    # clk_err = ResultData.Clock_Error
                    clk_err = check_clk_err(driver, dut)
                    print("final clk_err =", clk_err)

                    # pwr
                    if wlan_standard == '11b':
                        ResultData = driver.multiEval.modulation.dsss.average.fetch()
                        # evm=ResultData.Evm
                        evm = 20 * math.log((ResultData.Evm / 100), 10)
                        pwr = ResultData.Burst_Power
                        ResultData = driver.multiEval.modulation.dsss.maximum.fetch()
                        pwr_max = ResultData.Burst_Power
                        evm_max = 20 * math.log((ResultData.Evm / 100), 10)
                    else:
                        # pwr
                        ResultData = driver.multiEval.modulation.average.fetch()
                        pwr = ResultData.Burst_Power
                        # print(pwr)

                        # EVM
                        ResultData = driver.multiEval.modulation.ofdm.average.fetch()
                        evm = ResultData.Evm_All_Carr
                        # print(ResultData.Evm_All_Carr)

                        # ResultData.
                        driver.utilities.instrument_status_checking

                        ResultData = driver.multiEval.modulation.maximum.fetch()
                        pwr_max = ResultData.Burst_Power
                        evm_max = ResultData.Evm_All_Carr
                    diff_power = setpwr - pwr
                    diff_power_max = setpwr - pwr_max

                    # evm = round(evm, 1)
                    # pwr = round(pwr, 1)

                    ResultData_max = driver.multiEval.tsMask.maximum.fetch()
                    mask_abs_min = min(ResultData_max.Margin, key=abs)
                    ResultData_avg = driver.multiEval.tsMask.average.fetch()
                    ResultData_cur = driver.multiEval.tsMask.current.fetch()
                    len_data = len(ResultData_max.Margin)
                    for i in range(len_data):
                        if ResultData_max.Margin[i] > 0 or ResultData_avg.Margin[i] > 0 or ResultData_cur.Margin[i] > 0:
                            maskvalid = 'n'
                            break
                        else:
                            maskvalid = 'y'
                    mask_pass = maskvalid

                    #
                    data_dict['test_time'] = datetime.datetime.now().strftime("%m%d_%H%M%S")
                    data_dict["boardno"] = db_line.boardno()
                    data_dict["ant"] = db_line.ant()
                    data_dict["bin"] = db_line.binversion()
                    data_dict["freq"] = freq
                    data_dict["ch"] = ch
                    data_dict["rate"] = rate
                    data_dict["bw"] = bw
                    data_dict["setpwr"] = setpwr
                    data_dict["cmdx"] = cmdx
                    data_dict["pwr"] = round(pwr, 2)
                    data_dict["evm"] = round(evm, 2)
                    data_dict["pwr_max"] = round(pwr_max, 2)
                    data_dict["evm_max"] = round(evm_max, 2)
                    data_dict["clk_err"] = round(clk_err, 2)
                    data_dict["mask_abs_min"] = round(mask_abs_min, 2)
                    data_dict["mask_pass"] = mask_pass

                    # try:
                    #     data_dict["clk_err"] = round(clk_err, 2)
                    # except Exception as e:
                    #     data_dict["clk_err"] = None

                    dut.uart.send("settx 0")

                    # time.sleep(0.2)

                    # 打印字典
                    print("保存的数据行：", data_dict)
                    save_results(data_dict, file_path)

                    end_time = time.time()  # 记录结束时间
                    elapsed_time = end_time - start_time  # 计算耗时

                    print(f"code spand : {elapsed_time:.4f} s")  # 保留4位小数
