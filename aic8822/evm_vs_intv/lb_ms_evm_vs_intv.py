import os
import sys
import time

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *

global UARTc


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


if __name__ == "__main__":
    global UARTc

    UARTc = uart_open(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    """
    UARTc.sendcmd("setintv 50")
    time.sleep(4)
    CMPX.wlan_meas_start()
    time.sleep(2)
    evm_s = CMPX.wlan_meas_evm()
    pwr_s = CMPX.wlan_meas_pwr()
    CMPX.wlan_meas_abort()
    print("INTV 50: pwr, {}  evm, {}".format(pwr_s, evm_s))

    UARTc.sendcmd("setintv 100000")
    time.sleep(15)
    CMPX.wlan_meas_start()
    time.sleep(2)
    evm_l = CMPX.wlan_meas_evm()
    pwr_l = CMPX.wlan_meas_pwr()
    CMPX.wlan_meas_abort()
    print("INTV 10W: pwr, {}  evm, {}".format(pwr_l, evm_l))
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

    csv_name = "evm_pwr_vs_intv_20240606_1909.csv"

    colum_name = "iv_ib_mode, v_tc_mode, iv_it_mode, vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit, vl_i_itcgm_bit, vl_diode_en, evm_s, pwr_s, evm_l, pwr_l\n"
    with open(csv_name, "a+") as DATAX:
        DATAX.write(colum_name)

    datax.append(colum_name)

    for vm_cgm_ibit in range(7, 13, 1):   # 16
        for vm_vtr_ibit in range(0, 3, 1):   # 16
            for vl_i_itbg_bit in range(1, 4, 1):   # 8
                for vl_i_itcgm_bit in range(0, 3, 1):
                    for vl_diode_en in range(1, 4, 1):
                        """
                        vm_cgm_ibit = 8
                        vm_vtr_ibit = 0
                        vl_i_itbg_bit = 2
                        vl_i_itcgm_bit = 2
                        vl_diode_en = 3
                        """

                        UARTc.write_reg_mask("4034409c", "7:4", vm_cgm_ibit)  # def:15
                        UARTc.write_reg_mask("4034409C", "3:0", vm_vtr_ibit)  # def:0
                        UARTc.write_reg_mask("403440a0", "14:12", vl_i_itbg_bit)  # def:0
                        UARTc.write_reg_mask("403440a0", "11:9", vl_i_itcgm_bit)  # def:4
                        UARTc.write_reg_mask("403440a4", "31:29", vl_diode_en)    # def: 3
                        time.sleep(0.5)

                        """
                        CMPX.wlan_meas_start()
                        time.sleep(2)
                        pwrx = CMPX.wlan_meas_pwr()
                        CMPX.wlan_meas_abort()
                        # print(pwrx)
                        if float(pwrx) < 15:
                            data_linex = "{},{},{},{},{},{},{},{},{}\n".format(iv_ib_mode, v_tc_mode, iv_it_mode,
                                                                                vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit,
                                                                                vl_i_itcgm_bit, vl_diode_en, pwrx)
                            print(data_linex)
                            continue
                        """

                        # UARTc.sendcmd("settx 1")
                        # UARTc.sendcmd("setintv 50")
                        # time.sleep(3)
                        UARTc.sendcmd("settx 0")
                        # dpd recal
                        UARTc.sendcmd("calib 2 8000ff00 2 2442 0")
                        time.sleep(3)
                        # dpd use
                        UARTc.sendcmd("calib 2 8000ff00 1 2442 0")
                        # time.sleep(1)
                        UARTc.sendcmd("settx 1")

                        UARTc.sendcmd("setintv 50")
                        time.sleep(30)
                        CMPX.wlan_meas_start()
                        time.sleep(2)
                        evm_s = CMPX.wlan_meas_evm()
                        pwr_s = CMPX.wlan_meas_pwr()
                        CMPX.wlan_meas_abort()
                        if (float(evm_s) > -35) or (float(pwr_s) < 15):
                            print("{},{},{},{},{},{},{},{},{},{}\n".format(iv_ib_mode, v_tc_mode, iv_it_mode,
                                                                                vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit,
                                                                                vl_i_itcgm_bit, vl_diode_en, evm_s, pwr_s))
                            continue


                        UARTc.sendcmd("setintv 100000")
                        time.sleep(30)
                        CMPX.wlan_meas_start()
                        time.sleep(2)
                        evm_l = CMPX.wlan_meas_evm()
                        pwr_l = CMPX.wlan_meas_pwr()
                        CMPX.wlan_meas_abort()

                        data_line = "{},{},{},{},{},{},{},{},{},{},{},{}\n".format(iv_ib_mode, v_tc_mode, iv_it_mode,
                                                    vm_cgm_ibit, vm_vtr_ibit, vl_i_itbg_bit,
                                                    vl_i_itcgm_bit, vl_diode_en, evm_s, pwr_s, evm_l, pwr_l)
                        print(data_line)
                        datax.append(data_line)
                        with open(csv_name, "a+") as DATAX:
                            DATAX.write(data_line)