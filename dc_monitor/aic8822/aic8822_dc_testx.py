from dc_monitor.aic8822.msadc import *

from dc_monitor.SpecTable import *
from dc_monitor.BitsTable import *

global UARTc


def wf_tx0_on():
    UARTc.write_reg_mask("403441a4", "23:20", 14)


def wf_tx0_off():
    UARTc.write_reg_mask("403441a4", "23:20", 0)


def wf_rx0_on():
    UARTc.write_reg_mask("403441a4", "23:20", 11)


def wf_rx0_off():
    UARTc.write_reg_mask("403441a4", "23:20", 0)


def wf_tx1_on():
    UARTc.write_reg_mask("403441a8", "23:20", 14)


def wf_tx1_off():
    UARTc.write_reg_mask("403441a8", "23:20", 0)


def wf_rx1_on():
    UARTc.write_reg_mask("403441a8", "23:20", 11)


def wf_rx1_off():
    UARTc.write_reg_mask("403441a8", "23:20", 0)


def test_case_on(test_case):
    if test_case == "WF0_TX_ON":
        wf_tx0_on()
    elif test_case == "WF1_TX_ON":
        wf_tx1_on()
    elif test_case == "WF0_RX_ON":
        wf_rx0_on()
    elif test_case == "WF1_RX_ON":
        wf_rx1_on()


def test_case_off(test_case):
    if test_case == "WF0_TX_ON":
        wf_tx0_off()
    elif test_case == "WF1_TX_ON":
        wf_tx1_off()
    elif test_case == "WF0_RX_ON":
        wf_rx0_off()
    elif test_case == "WF1_RX_ON":
        wf_rx1_off()


def measure_dc_by_channel(db_nets_by_channel):
    for db_net in db_nets_by_channel:
        cmd_str = ""
        if db_net.enable_reg_name in aic8822_bits_dict.keys() and db_net.mode_reg_name in aic8822_bits_dict.keys() and db_net.bits_reg_name in aic8822_bits_dict.keys():
            cmd_str = cmd_str + db_net.name + ","

            # 1 test on
            test_case_on(db_net.test_case)
            cmd_str = cmd_str + db_net.test_case + "_ON,"

            # 2 test enable
            enable_bit_reg_address = aic8822_bits_dict[db_net.enable_reg_name].address
            enable_bit_pos = aic8822_bits_dict[db_net.enable_reg_name].pos
            UARTc.write_reg_mask(enable_bit_reg_address, enable_bit_pos, db_net.enable_reg_value)
            cmd_str = cmd_str + enable_bit_reg_address + " " + enable_bit_pos + " " + str(db_net.enable_reg_value) + ","

            # 3 test mode
            mode_bit_reg_addrss = aic8822_bits_dict[db_net.mode_reg_name].address
            mode_bit_pos = aic8822_bits_dict[db_net.mode_reg_name].pos
            UARTc.write_reg_mask(mode_bit_reg_addrss, mode_bit_pos, db_net.mode_reg_value)
            cmd_str = cmd_str + mode_bit_reg_addrss + " " + mode_bit_pos + " " + str(db_net.mode_reg_value) + ","

            # 4 test bit
            test_bit_reg_addrss = aic8822_bits_dict[db_net.bits_reg_name].address
            test_bit_pos = aic8822_bits_dict[db_net.bits_reg_name].pos
            UARTc.write_reg_mask(test_bit_reg_addrss, test_bit_pos, db_net.bits_reg_value)
            cmd_str = cmd_str + test_bit_reg_addrss + " " + test_bit_pos + " " + str(db_net.bits_reg_value) + ","

            # 5 measure dc
            volt = msadcx.ms_volt()*1000.0
            cmd_str = cmd_str + "MSADC_MS_DC" + ","

            # 6 test enable off
            UARTc.write_reg_mask(enable_bit_reg_address, enable_bit_pos, 0)
            cmd_str = cmd_str + enable_bit_reg_address + " " + enable_bit_pos + " 0" + ","

            # x test case off
            test_case_off(db_net.test_case)
            cmd_str = cmd_str + db_net.test_case + "_OFF\n"

            datax.append(db_net.name + "," + str(volt) + "\n")
        else:
            datax.append(db_net.name + "," + "ERROR: reg name not found" + "\n")
            cmd_str = cmd_str + db_net.name + ", ERROR: reg name not found!!! \n"
        ms_cmd.append(cmd_str)


if __name__ == "__main__":
    global UARTc

    UARTc = uart_open(7)
    UARTc.open()

    msadcx = MSADC(clk_div=30, acc_mode=1, adc_id=1)
    msadcx.basiconfig()
    msadcx.adconfig()
    msadcx.input_sel_testport()

    spec_table_path = "./MsTables/aic8822_spec_testability_20240730.csv"
    aic8822_spec = SpecTable(spec_table_path)
    bits_table_path = "./MsTables/aic8822_bits_table.csv"
    aic8822_bits = BitsTable(bits_table_path)
    aic8822_bits_dict = aic8822_bits.bits_dict()

    datax = []

    ms_cmd = ["MSADC_BASICONFIG, MSADC_ADCONFIG, MSADC_INPUT_SEL_TESTPORT\n"]
    ms_cmd.append("setch 7, setrate 5 0, setpwr 14, settx 1, settx 0\n")
    UARTc.sendcmd("setch 7")
    UARTc.sendcmd("setrate 5 11")
    UARTc.sendcmd("setpwr 14")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")
    time.sleep(8)
    measure_dc_by_channel(aic8822_spec.db_nets_by_band("WF_LB"))

    with open("./MsDatas/aic8822_test_lb_dc_20240731.csv", "a+") as CSVFILE:
        CSVFILE.writelines(datax)

    """
    ms_cmd.append("setch 100, setrate 5 0, setpwr 14, settx 1, settx 0\n")
    UARTc.sendcmd("setch 100")
    UARTc.sendcmd("setrate 5 1")
    UARTc.sendcmd("setpwr 14")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")
    time.sleep(8)
    measure_dc_by_channel(aic8822_spec.db_nets_by_band(["WF_HB", "WF", "CM"]))

    ms_cmd.append("setch 6500\n")
    UARTc.sendcmd("setch 6500")
    time.sleep(8)
    measure_dc_by_channel(aic8822_spec.db_nets_by_band("WF_6E"))

    UARTc.close()

    with open("aic8822_test_hb1_pwr_20240619.csv", "a+") as CSVFILE:
        CSVFILE.writelines(datax)

    with open("aic8822_test_cmd_20240619.csv", "w") as CMDX:
        CMDX.writelines(ms_cmd)
    """
