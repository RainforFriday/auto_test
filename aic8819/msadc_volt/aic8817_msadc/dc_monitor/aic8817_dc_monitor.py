import os
import sys
import time

from icbasic.aicbasic import *
from icbasic.aicintf.uart import *
from msadc import *

from SpecTable import *
from BitsTable import *
from aicintf.uart import *
global UARTc
def wf_tx_on():
    UARTc.write_reg_mask("40344078", "3:2", 3)
    UARTc.write_reg_mask("40344078", "1:0", 2)

def wf_tx_off():
    UARTc.write_reg_mask("40344078", "3:2", 2)


def wf_rx_on():
    UARTc.write_reg_mask("40344078", "1:0", 3)
    UARTc.write_reg_mask("40344078", "3:2", 2)

def wf_rx_off():
    UARTc.write_reg_mask("40344078", "1:0", 2)



def test_case_on(test_case):
    if test_case == "WF_TX_ON":
        wf_tx_on()
    elif test_case == "WF_RX_ON":
        wf_rx_on()
    else:
        pass


def test_case_off(test_case):
    if test_case == "WF_TX_ON":
        wf_tx_off()
    elif test_case == "WF_RX_ON":
        wf_rx_off()
    else:
        pass

def measure_dc_by_channel(db_nets_by_channel):
    #print(db_net)
    #print(db_nets_by_channel)

    for db_net in db_nets_by_channel:
        #print(db_net)
        cmd_str = ""
        a=0
        aic8817_bits_dict[" "]=" "
        #print(db_net.mode_reg_name)
        if db_net.mode_reg_name=="":
            a=1
        #print(db_net.enable_reg_name)
        #print(aic8817_bits_dict.keys())
        #print(db_net.mode_reg_name)
        #print(aic8817_bits_dict.keys())
        #print(db_net.bits_reg_name)
        #print(aic8817_bits_dict.keys())
        if db_net.enable_reg_name in aic8817_bits_dict.keys() and db_net.mode_reg_name in aic8817_bits_dict.keys() and db_net.bits_reg_name in aic8817_bits_dict.keys():
            cmd_str = cmd_str + db_net.name + ","

            # 1 test on
            test_case_on(db_net.test_case)
            cmd_str = cmd_str + db_net.test_case + "_ON,"
            #print(cmd_str)

            # 2 test enable
            enable_bit_reg_address = aic8817_bits_dict[db_net.enable_reg_name].address
            enable_bit_pos = aic8817_bits_dict[db_net.enable_reg_name].pos
            UARTc.write_reg_mask(enable_bit_reg_address, enable_bit_pos, db_net.enable_reg_value)
            cmd_str = cmd_str + enable_bit_reg_address + " " + enable_bit_pos + " " + str(db_net.enable_reg_value) + ","



            # 3 test mode
            if a==0:
                mode_bit_reg_addrss = aic8817_bits_dict[db_net.mode_reg_name].address
                mode_bit_pos = aic8817_bits_dict[db_net.mode_reg_name].pos
                UARTc.write_reg_mask(mode_bit_reg_addrss, mode_bit_pos, db_net.mode_reg_value)
                cmd_str = cmd_str + mode_bit_reg_addrss + " " + mode_bit_pos + " " + str(db_net.mode_reg_value) + ","

            # 4 test bit
            test_bit_reg_addrss = aic8817_bits_dict[db_net.bits_reg_name].address
            test_bit_pos = aic8817_bits_dict[db_net.bits_reg_name].pos
            UARTc.write_reg_mask(test_bit_reg_addrss, test_bit_pos, db_net.bits_reg_value)
            cmd_str = cmd_str + test_bit_reg_addrss + " " + test_bit_pos + " " + str(db_net.bits_reg_value) + ","

            #7 test_lvl_en
            if db_net.test_band=="":
                pass
            else:
                #print(3)
                test_lvl_reg_addrss=aic8817_bits_dict[db_net.test_band.split("=")[0]].address
                test_lvl_pos = aic8817_bits_dict[db_net.test_band.split("=")[0]].pos
                UARTc.write_reg_mask(test_lvl_reg_addrss, test_lvl_pos, db_net.test_band.split("=")[1])
                cmd_str = cmd_str + test_lvl_reg_addrss + " " + test_lvl_pos + " " + str(db_net.test_band.split("=")[1]) + ","
            # 5 measure dc
            volt = msadcx.ms_volt()*1000.0
            cmd_str = cmd_str + "MSADC_MS_DC" + ","

            # 6 test enable off
            UARTc.write_reg_mask(enable_bit_reg_address, enable_bit_pos, 0)
            cmd_str = cmd_str + enable_bit_reg_address + " " + enable_bit_pos + " 0" + ","

            # test lvl off
            if db_net.test_band=="":
                pass
            else:
                test_lvl_reg_addrss=aic8817_bits_dict[db_net.test_band.split("=")[0]].address
                test_lvl_pos = aic8817_bits_dict[db_net.test_band.split("=")[0]].pos
                UARTc.write_reg_mask(test_lvl_reg_addrss, test_lvl_pos, 0)
                cmd_str = cmd_str + test_lvl_reg_addrss + " " + test_lvl_pos + " 0" + ","
            # x test case off
            test_case_off(db_net.test_case)
            cmd_str = cmd_str + db_net.test_case + "_OFF\n"
            print(db_net.name + ","+db_net.block.rsplit("_") [0]+","+ str(volt))
            with open(test_data_path, "a+") as CSVFILE:
                CSVFILE.writelines(db_net.name + ","+db_net.block.rsplit("_") [0]+","+ str(volt)+ "\n")
        else:
            datax.append(db_net.name + "," + "ERROR: reg name not found" + "\n")
            cmd_str = cmd_str + db_net.name + ", ERROR: reg name not found!!! \n"
        ms_cmd.append(cmd_str)

def wf_init():
    UARTc.sendcmd("setch 7")
    time.sleep(1)
    UARTc.sendcmd("setrate 2 0")
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd("setpwr 3")
    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")
    time.sleep(1)

if __name__ == "__main__":
    global UARTc,block_sel,datax,msadcx,test_data_path
    UARTc = uart_open(3,1417846)
    msadcx = MSADC()
    spec_table_path = "./aic8817/aic8817_spec_testability20251231.csv"
    aic8817_spec = SpecTable(spec_table_path)
    bits_table_path = "./aic8817/aic8817_bits_table.csv"
    aic8817_bits = BitsTable(bits_table_path)
    aic8817_bits_dict = aic8817_bits.bits_dict()
    test_data_path= "test_data/aic8817_test_260114_all_tempm45_0.csv"
    ms_cmd = ["MSADC_BASICONFIG, MSADC_ADCONFIG, MSADC_INPUT_SEL_TESTPORT\n"]
   # ms_cmd.append("setch 7, setrate 2 0,pwrmm 1, setpwr 3, settx 1, settx 0\n")
    #wf_init()

    #print(aic8817_spec.db_nets_by_block("lna"))
    msadcx.ms_portdc_config()
    measure_dc_by_channel(aic8817_spec.db_nets_by_block(["mdll", "vco", "bbpll", "rfpll"]))
        # block_sel = ["pa_hb0", "pa_lb0"]
        # block_sel = "pa_hb0"
        # block_sel = "all"
        # block_sel = "pa"
    with open("test_data\\aic8817_test_cmd_202601142016.csv", "w") as CMDX:
        CMDX.writelines(ms_cmd)
    UARTc.close()

