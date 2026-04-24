import serial   # pip install pyserial
import serial.tools.list_ports
import re
import sys
import pyprind
import xmodem
from aicintf.uart import *
from aicintf.com import *
from aicbasic.aiclog import *
from aic8820.msadc import *
sys.path.append("..")


def wakeup_and_test_tia_dc(agc):
    flag_error = 0
    uart0.write_reg_mask("40344088", "20:19", 3)  # rx on
    time.sleep(0.1)
    # wake up tia
    uart0.write_reg_mask("40344000", "23:22", 3)  # pu_tia_dr=1
    uart0.write_reg_mask("40344088", "13:10", 15)  # fixed to AGC-F
    uart0.write_reg_mask("40344088", "18", 1)
    uart0.write_reg_mask("4034409c", "3:0", 8)  # tia_gbit_dr = 1, tia_gbit = 0
    uart0.write_reg("40344094", 0x23)
    uart0.write_reg("40344094", 0x3)
    uart0.write_reg("40344094", 0x43)
    uart0.write_reg("40344094", 0x53)
    uart0.write_reg_mask("403469e0", "30:28", 0)  # rmx_cload_bit = 0
    uart0.write_reg("40344094", 0x13)
    uart0.write_reg("40344094", 0x3)
    uart0.write_reg("40344094", 0x23)
    uart0.write_reg("40344094", 0x33)
    uart0.write_reg_mask("40344088", "20:19", 2)  # rx off
    uart0.write_reg_mask("40344088", "20:19", 3)  # rx on
    uart0.write_reg_mask("40344088", "13:10", agc)
    uart0.write_reg_mask("40344088", "18", 1)
    uart0.write_reg_mask("4034409c", "3:0", 0)  # tia_gbit_dr = 0
    # measure
    uart0.write_reg_mask("4034400C", "27:26", 1)  # turn on test_enable_tia
    uart0.write_reg_mask("40344008", "2:0", 4)  # set wf_test_bit
    tia_i_ip = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 5)  # set wf_test_bit
    tia_i_in = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 6)  # set wf_test_bit
    tia_q_ip = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 7)  # set wf_test_bit
    tia_q_in = adc.ms_portdc()
    uart0.write_reg_mask("4034400C", "27:26", 2)  # turn off test_enable_tia
    uart0.write_reg_mask("40344008", "2:0", 4)  # set wf_test_bit
    tia_i_op = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 5)  # set wf_test_bit
    tia_i_on = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 6)  # set wf_test_bit
    tia_q_op = adc.ms_portdc()
    uart0.write_reg_mask("40344008", "2:0", 7)  # set wf_test_bit
    tia_q_on = adc.ms_portdc()
    uart0.write_reg_mask("4034400C", "27:26", 0)  # turn off test_enable_tia
    # analyze
    i_in_error = (tia_i_ip < 600 or tia_i_ip > 740 or tia_i_in < 600 or tia_i_in > 740)
    q_in_error = (tia_q_ip < 600 or tia_q_ip > 740 or tia_q_in < 600 or tia_q_in > 740)
    i_out_error = (tia_i_op < 600 or tia_i_op > 740 or tia_i_on < 600 or tia_i_on > 740)
    q_out_error = (tia_q_op < 600 or tia_q_op > 740 or tia_q_on < 600 or tia_q_on > 740)
    print('tia_i_ip : %.1f  mV' % tia_i_ip)
    print('tia_i_in : %.1f  mV' % tia_i_in)
    print('tia_i_op : %.1f  mV' % tia_i_op)
    print('tia_i_on : %.1f  mV' % tia_i_on)
    print('tia_q_ip : %.1f  mV' % tia_q_ip)
    print('tia_q_in : %.1f  mV' % tia_q_in)
    print('tia_q_op : %.1f  mV' % tia_q_op)
    print('tia_q_on : %.1f  mV' % tia_q_on)
    if i_in_error or q_in_error or i_out_error or q_out_error:
        flag_error = 1
    uart0.write_reg_mask("40344088", "20:19", 2)  # rx off
    uart0.write_reg_mask("40344000", "23:22", 2)  # power off tia and dr=0
    uart0.write_reg_mask("40344000", "23:22", 0)  # power off tia and dr=0
    time.sleep(0.01)
    return flag_error


if __name__ == "__main__":
    comport = 14
    uart0 = uart_open(comport)
    adc = MSADC(clk_div=80, acc_mode=0)

    uart0.write_reg_mask("40344088", "17:14", 12)
    flag_x = 0
    for xi in range(14):
        flag_x = wakeup_and_test_tia_dc(xi)
        if flag_x == 1:
            print('Fail @ AGC: %d' % xi)
            print('Bad Die!')
            break
        else:
            print('Pass @ AGC: %d' % xi)
    if flag_x == 0:
        print('Pass All AGC Gears ^_^')
        print('Good Die!')

    uart_close()