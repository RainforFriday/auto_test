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


def load_bin(UART2,bin_file_path):
    UART2.xmodem_load_bin("x 160000", bin_file_path)
    xxx = UART2.sendcmd("g 160000")
    print(xxx)



def check_clk_err(driver, dut, max_try=3):
    """
    检查 clk_err，尝试修正，最多 max_try 次。
    返回最后一次测得的 clk_err（无论是否成功）。
    """
    clk_err = float('nan')
    try:
        for attempt in range(1, max_try + 1):
            # 获取测量结果
            driver.utilities.query_opc()
            ResultData = driver.multiEval.modulation.average.fetch()
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
                UARTc.sendcmd(cmd)
                driver.multiEval.stop()
                driver.multiEval.initiate()
                device.wait_ms(2000)

        # 如果执行完 max_try 次仍未成功，返回最后的 clk_err
        # driver.multiEval.initiate()
        driver.utilities.query_opc()
        print("❌ 失败：多次尝试后仍未成功")
        return clk_err
    except Exception as e:
        clk_err = float('nan')
        driver.multiEval.stop()
        driver.multiEval.initiate()
        driver.utilities.query_opc()
    return clk_err

def get_limit(driver, wlan_standard):
    ResultData = driver.multiEval.modulation.standardDev.fetch()
    modulation = ResultData.Mod_Type
    if wlan_standard == '11b':
        evm_rms_limit = driver.configure.multiEval.limit.modulation.dsss.get_evm_ems()
        limit = 20 * math.log((evm_rms_limit / 100), 10)
    elif wlan_standard == '11n':
        EvmStruct = driver.configure.multiEval.limit.modulation.htOfdm.get_evm()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmStruct.Evm_Q_1_M_12
        elif modulation == enums.ModulationTypeD._64Q12:
            limit = EvmStruct.Evm_Q_6_M_12
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = EvmStruct.Evm_Q_6_M_34
        else:
            limit = EvmStruct.Evm_Q_6_M_56
    elif wlan_standard == '11a':
        EvmStruct = driver.configure.multiEval.limit.modulation.lofdm.get_evm()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmStruct.Evm_6_M
        elif modulation == enums.ModulationTypeD.BPSK34:
            limit = EvmStruct.Evm_9_M
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmStruct.Evm_12_M
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmStruct.Evm_18_M
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmStruct.Evm_24_M
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = EvmStruct.Evm_36_M
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = EvmStruct.Evm_48_M
        else:
            limit = EvmStruct.Evm_54_M

    elif wlan_standard == '11ac':
        EvmAllStruct = driver.configure.multiEval.limit.modulation.vhtOfdm.get_evm_all()
        if modulation == enums.ModulationTypeD.BPSK12:
            limit = EvmAllStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = EvmAllStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = EvmAllStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = EvmAllStruct.Evm_16_Qam_12
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = EvmAllStruct.Evm_16_Qam_34
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = EvmAllStruct.Evm_64_Qam_12
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = EvmAllStruct.Evm_64_Qam_34
        elif modulation == enums.ModulationTypeD._64Q56:
            limit = EvmAllStruct.Evm_64_Qam_56
        elif modulation == enums.ModulationTypeD._256Q34:
            limit = EvmAllStruct.Evm_256_Qam_34
        elif modulation == enums.ModulationTypeD._256Q56:
            limit = EvmAllStruct.Evm_256_Qam_56
        elif modulation == enums.ModulationTypeD._1KQ34:
            limit = EvmAllStruct.Evm_1024_Qam_34
        else:
            limit = EvmAllStruct.Evm_1024_Qam_56
    else:
        ValueStruct = driver.configure.multiEval.limit.modulation.heOfdm.evmAll.get_value()
        if modulation == enums.ModulationTypeD.BPSK14:
            limit = ValueStruct.Evm_Br_14
        elif modulation == enums.ModulationTypeD.BPSK12:
            limit = ValueStruct.Evm_Br_12
        elif modulation == enums.ModulationTypeD.QPSK14:
            limit = ValueStruct.Evm_Qr_14
        elif modulation == enums.ModulationTypeD.QPSK12:
            limit = ValueStruct.Evm_Qr_12
        elif modulation == enums.ModulationTypeD.QPSK34:
            limit = ValueStruct.Evm_Qr_34
        elif modulation == enums.ModulationTypeD._16Q14:
            limit = ValueStruct.Evm_16_Qam_14
        elif modulation == enums.ModulationTypeD._16Q38:
            limit = ValueStruct.Evm_16_Qam_38
        elif modulation == enums.ModulationTypeD._16Q12:
            limit = ValueStruct.Evm_16_Qam_12
        elif modulation == enums.ModulationTypeD._16Q34:
            limit = ValueStruct.Evm_16_Qam_34
        elif modulation == enums.ModulationTypeD._64Q23:
            limit = ValueStruct.Evm_64_Qam_23
        elif modulation == enums.ModulationTypeD._64Q34:
            limit = ValueStruct.Evm_64_Qam_34
        elif modulation == enums.ModulationTypeD._64Q56:
            limit = ValueStruct.Evm_64_Qam_56
        elif modulation == enums.ModulationTypeD._256Q34:
            limit = ValueStruct.Evm_256_Qam_34
        elif modulation == enums.ModulationTypeD._256Q56:
            limit = ValueStruct.Evm_256_Qam_56
        elif modulation == enums.ModulationTypeD._1KQ34:
            limit = ValueStruct.Evm_1024_Qam_34
        else:
            limit = ValueStruct.Evm_1024_Qam_56
    return limit

def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc

if __name__ == "__main__":

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_all_sample.xlsx'
    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_pwr_verify.xlsx'
    xlsx_path = r'D:\PyProject\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_pwr.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # file_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\Tuner_swp_data_20250805.csv'
    # file_path = r'D:\PyProject\AIC_TEST\aic8819\CMW_test\data\260123\8822_pwr_ai_link_chip_0.3pf_1.1nh_nc_5G_'+current_time+'.xlsx'
    file_path = r'D:\PyProject\AIC_TEST\aic8819\CMW_test\data\260123\8822_pwr_ai_link_chip_0.3pf_1.1nh_nc_5G'+current_time+'_ant0.xlsx'

    RsCmwWlanMeas.assert_minimum_version('3.8.20')
    resource_string_1 = 'TCPIP0::192.168.31.11::INSTR'  # Standard LAN connection (also called VXI-11)
    # resource_string_1 = 'TCPIP0::CMW50050-106146::inst1::INSTR'  # Standard LAN connection (also called VXI-11)
    # Initializing the session
    driver = RsCmwWlanMeas(resource_string_1)
    idn = driver.utilities.query_str('*IDN?')
    print(f"\nHello, I am: '{idn}'")



    UARTc = uart_open(20)
    bin_ver = 'testmode_8800d80x2.bin'



    # # once
    # UARTc.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = "./bin/" + bin_ver
    # load_bin_X10(UARTc, bin_file_path)
    # time.sleep(1)

    data_dict = {}


    # UARTc.sendcmd("settx 0")
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd("setintv 500")

    table_lines = WF_MS_TABLE(xlsx_path).read()
    with tqdm(total=(len(table_lines))) as pbar:
        for linex in table_lines:
            db_line = WF_MS_LINE(linex)
            if db_line.enable() not in ["Y", "y", "YES", "yes"]:
                continue

            UARTc.sendcmd(db_line.setlen_ucmd())
            UARTc.sendcmd(db_line.setrate_ucmd())
            UARTc.sendcmd(db_line.setbw_ucmd())
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
                    wlan_standard = "11a"

            # driver.configure.rfSettings.eattenuation.set(10, connector=repcap.Connector.Default)

            # config std bw
            if wlan_standard == '11b':
                driver.configure.isignal.set_standard(enums.IeeeStandard.DSSS)
            elif wlan_standard == '11a':
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
                if int(ch) < 15:
                    driver.configure.rfSettings.eattenuation.set(0.7, connector=repcap.Connector.Default)
                elif (int(ch) > 30) and (int(ch) < 170):
                    driver.configure.rfSettings.eattenuation.set(1.2, connector=repcap.Connector.Default)
                else:
                    print("wrong ch selected!!!")
                    time.sleep(60)
                UARTc.sendcmd(setchx)
                time.sleep(2)

                # if ch > 35:
                #     channel = (5180 + (ch - 36) * 5) * 1000000.0
                # else:
                #     channel = (2412 + (ch - 1) * 5) * 1000000.0
                # device.wait_ms(10)
                driver.configure.rfSettings.frequency.set_value(frequency=freq*1e6)
                device.wait_ms(500)

                # UARTc.sendcmd("pwrmm 1")
                for setpwrx in db_line.l_setpwr_ucmd():
                    start_time = time.time()

                    setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                    setpwr = int(setpwr)
                    UARTc.sendcmd(setpwrx)
                    UARTc.sendcmd("settx 1")

                    cmdx = ""
                    # print(db_line.l_uartcmd())
                    try:
                        if db_line.l_uartcmd() is not None:
                            for u_cmdx in db_line.l_uartcmd():
                                # cmdx = cmdx + UARTc.sendcmd(u_cmdx)
                                cc2 = UARTc.sendcmd(u_cmdx)
                                cmdx = cc2.split('\n')[1].strip()

                                # print(cmdx)
                    except:
                        cmdx = "ERROR"

                    for key_str in [",", "\n", "\r", "aic>"]:
                        cmdx = cmdx.replace(key_str, " ")

                    time.sleep(0.2)

                    exp_pwr_con = setpwr + 14
                    driver.configure.rfSettings.envelopePower.set(min(exp_pwr_con, 33), connector=repcap.Connector.Default)

                    # device.wait_ms(100) upadte
                    driver.multiEval.stop()
                    driver.multiEval.initiate()
                    device.wait_ms(1000)
                    driver.utilities.query_opc()

                    # # Clock_Error
                    # # ResultData = driver.multiEval.modulation.average.fetch()
                    # # clk_err = ResultData.Clock_Error

                    # clk_err = check_clk_err(driver, dut)
                    # print("final clk_err =", clk_err)

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
                        # ResultData = driver.multiEval.modulation.average.fetch()
                        # pwr =
                        # res = driver.utilities.query_str('FETCh:WLAN:MEASurement:MEValuation:MODulation:AVERage?')
                        # pwr = res.split(",")[12]

                        max_retries = 3
                        for attempt in range(max_retries):

                            try:
                                res = driver.utilities.query_str('FETCh:WLAN:MEASurement:MEValuation:MODulation:AVERage?')
                                pwr = float(res.split(",")[12])
                            except ValueError:
                                pwr = -100.00
                            # print(pwr)

                            if float(pwr) > -20.0:
                                break
                            print_red(f"failed, again!")
                            UARTc.sendcmd(setchx)
                            time.sleep(2)
                            # CMPX.wlan_meas_abort()
                            UARTc.sendcmd(setpwrx)
                            UARTc.sendcmd("settx 1")


                        # EVM
                        ResultData = driver.multiEval.modulation.ofdm.average.fetch()
                        # pwr = ResultData.Burst_Power
                        evm = ResultData.Evm_All_Carr
                        # print(ResultData.Evm_All_Carr)

                        # ResultData = driver.multiEval.modulation.maximum.fetch()
                        # pwr_max = ResultData.Burst_Power
                        # evm_max = ResultData.Evm_All_Carr
                    diff_power = setpwr - pwr
                    # diff_power_max = setpwr - pwr_max

                    # evm_limit = get_limit(driver, wlan_standard)

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
                    end_time = time.time()  # 记录结束时间
                    elapsed_time = end_time - start_time  # 计算耗时

                    print(f"code spand : {elapsed_time:.4f} s")  # 保留4位小数

                    # data_dict['test_time'] = datetime.datetime.now().strftime("%m%d_%H%M%S")
                    data_dict['test_time'] = elapsed_time
                    data_dict["boardno"] = db_line.boardno()
                    data_dict["ant"] = db_line.ant()
                    data_dict["bin"] = bin_ver
                    data_dict["freq"] = freq
                    data_dict["ch"] = ch
                    data_dict["format"] = wlan_standard
                    data_dict["rate"] = rate
                    data_dict["bw"] = bw
                    data_dict["setpwr"] = setpwr
                    data_dict["cmdx"] = cmdx
                    data_dict["pwr"] = round(pwr, 2)
                    data_dict["evm"] = round(evm, 2)
                    # data_dict["avg_pwr"] = round(pwr_max, 2)
                    # data_dict["evm"] = round(evm_max, 2)
                    # data_dict["evm_limit"] = evm_limit

                    # data_dict["clk_err"] = round(clk_err, 2)
                    # data_dict["mask_abs_min"] = round(mask_abs_min, 2)
                    # data_dict["mask_pass"] = mask_pass

                    # try:
                    #     data_dict["clk_err"] = round(clk_err, 2)
                    # except Exception as e:
                    #     data_dict["clk_err"] = None

                    # time.sleep(0.2)

                    # 打印字典
                    print("保存的数据行：", data_dict)
                    save_results(data_dict, file_path)

                UARTc.sendcmd("settx 0")

    driver.close()
    # dut.uart
