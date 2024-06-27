import os
import sys
import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from msadc import *

global UARTc

"""
def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()

"""


def wf_tx0_on():
    UARTc.write_reg_mask("403441a4", "23:20", 14)


def wf_tx0_off():
    UARTc.write_reg_mask("403441a4", "23:20", 0)


if __name__ == "__main__":
    global UARTc

    UARTc = uart_open(7)
    UARTc.open()

    msadcx = MSADC(clk_div=30, acc_mode=1, adc_id=1)
    msadcx.basiconfig()
    msadcx.adconfig()
    msadcx.input_sel_testport()

    """
    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)
    """


    iv_ib_mode = 6
    v_tc_mode = 0
    iv_it_mode = 3

    # lb0 iv_ib_mode, def value: 4
    UARTc.write_reg_mask("403440a4", "16:14", iv_ib_mode)

    # lb0 v_tc_mode, def value: 0
    UARTc.write_reg_mask("403440a4", "28:26", v_tc_mode)

    # lb0 iv_it_mode, def value: 3
    UARTc.write_reg_mask("403440a0", "2:0", iv_it_mode)

    datax = []

    csv_name = "lb_vm_vl_20240605_1629.csv"

    colum_name = "iv_ib_mode, v_tc_mode, iv_it_mode, vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit, vl_i_itcgm_bit, vl_diode_en, evm_s, pwr_s, evm_l, pwr_l\n"
    with open(csv_name, "a+") as DATAX:
        DATAX.write(colum_name)

    datax.append(colum_name)



    wf_tx0_on()

    # test_enable
    UARTc.write_reg_mask("40344024", "18", 1)
    # test_mode
    UARTc.write_reg_mask("40502018", "8:7", 3)

    for vm_cgm_ibit in range(12, 16, 2):   # max: 16, def : 12
        for vm_vtr_ibit in range(0, 3, 2):   # max: 15, def : 1
            for vl_i_itbg_bit in range(0, 8, 2):   # 8
                for vl_i_itcgm_bit in range(0, 8, 2):
                    for vl_diode_en in range(0, 8, 2):

                        UARTc.write_reg_mask("4034409c", "7:4", vm_cgm_ibit)  # def:15
                        UARTc.write_reg_mask("4034409C", "3:0", vm_vtr_ibit)  # def:0
                        UARTc.write_reg_mask("403440a0", "14:12", vl_i_itbg_bit)  # def:0
                        UARTc.write_reg_mask("403440a0", "11:9", vl_i_itcgm_bit)  # def:4
                        UARTc.write_reg_mask("403440a4", "31:29", vl_diode_en)    # def: 3


                        # vl
                        UARTc.write_reg_mask("40502018", "17:15", 3)
                        vl = msadcx.ms_volt() * 1000.0

                        # vm
                        UARTc.write_reg_mask("40502018", "17:15", 4)
                        vm = msadcx.ms_volt() * 1000.0 *2.0

                        data_line = "{},{},{},{},{},{},{},{},{:.2f},{:.2f}\n".format(iv_ib_mode, v_tc_mode, iv_it_mode,
                                                    vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit,
                                                    vl_i_itcgm_bit, vl_diode_en, vl, vm)
                        print(data_line)
                        datax.append(data_line)
                        with open(csv_name, "a+") as DATAX:
                            DATAX.write(data_line)
