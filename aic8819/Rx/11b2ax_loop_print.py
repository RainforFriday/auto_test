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


if __name__ == "__main__":

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\CMW_test\Table\cmw_TABLE_all_sample.xlsx'
    xlsx_path = r'.\Table\cmw_TABLE_pwr.xlsx'

    RsCmwWlanMeas.assert_minimum_version('3.8.20')
    resource_string_1 = 'TCPIP0::10.21.10.130::INSTR'  # Standard LAN connection (also called VXI-11)
    # resource_string_1 = 'TCPIP0::CMW50050-170904::inst1::INSTR'  # Standard LAN connection (also called VXI-11)
    # Initializing the session
    driver = RsCmwWlanMeas(resource_string_1)
    idn = driver.utilities.query_str('*IDN?')
    print(f"\nHello, I am: '{idn}'")

    UARTX = Uart(18, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()
    
    bin_file = "testmode19_2025_1010_1230.bin"
    # bin_file = "testmode19_2025_1014_1831.bin"
    # bin_file = "testmode19_2025_1014_1831_phydump256k.bin"

    # # once
    UARTX.sendcmd('reboot')
    time.sleep(2)
    bin_file_path = './bin/'+bin_file
    load_bin_X10(UARTX, bin_file_path)

    data_dict = {}

    UARTX.sendcmd("pwrmm 1")
    UARTX.sendcmd("setintv 500")

    table_lines = WF_MS_TABLE(xlsx_path).read()

    for linex in table_lines:
        db_line = WF_MS_LINE(linex)
        if db_line.enable() not in ["Y", "y", "YES", "yes"]:
            continue

        UARTX.sendcmd(db_line.setlen_ucmd())
        UARTX.sendcmd(db_line.setrate_ucmd())
        UARTX.sendcmd(db_line.setbw_ucmd())
        rate = " ".join(db_line.setrate_ucmd().strip().split(" ")[1:])
        bw = " ".join(db_line.setbw_ucmd().strip().split(" ")[1:])
        len_set = " ".join(db_line.setlen_ucmd().strip().split(" ")[1:])

        for setchx in db_line.l_setch_ucmd():
            ch = setchx.strip().split(" ")[1]
            freq = get_freq_by_ch(ch)
            UARTX.sendcmd(setchx)
            time.sleep(2)

            UARTX.sendcmd("pwrmm 1")
            for setpwrx in db_line.l_setpwr_ucmd():
                start_time = time.time()

                setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                setpwr = int(setpwr)
                UARTX.sendcmd(setpwrx)
                UARTX.sendcmd("settx 1")

                while time.time() - start_time < 3:
                    # 读取一行数据
                    if UARTX.ser.in_waiting > 0:
                        line = UARTX.ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(line)


            # UARTX.sendcmd("pwrmm 0")
            UARTX.sendcmd("settx 0")

    driver.close()
