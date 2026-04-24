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


def test_tia_dc():
    flag_error = 0
    # rx on
    uart0.write_reg_mask("40344088", "20:19", 3)
    time.sleep(0.1)
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
    i_in_error = (tia_i_ip < 600 or tia_i_ip > 720 or tia_i_in < 600 or tia_i_in > 720)
    q_in_error = (tia_q_ip < 600 or tia_q_ip > 720 or tia_q_in < 600 or tia_q_in > 720)
    i_out_error = (tia_i_op < 600 or tia_i_op > 720 or tia_i_on < 600 or tia_i_on > 720)
    q_out_error = (tia_q_op < 600 or tia_q_op > 720 or tia_q_on < 600 or tia_q_on > 720)
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
    # rx off
    uart0.write_reg_mask("40344088", "20:19", 2)
    time.sleep(0.01)
    return flag_error


def scan_tia_dc():
    flag_error = 0
    for i in range(10):
        # rx on
        uart0.write_reg_mask("40344088", "20:19", 3)
        time.sleep(0.1)
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
        i_in_error = (tia_i_ip < 600 or tia_i_ip > 720 or tia_i_in < 600 or tia_i_in > 720)
        q_in_error = (tia_q_ip < 600 or tia_q_ip > 720 or tia_q_in < 600 or tia_q_in > 720)
        i_out_error = (tia_i_op < 600 or tia_i_op > 720 or tia_i_on < 600 or tia_i_on > 720)
        q_out_error = (tia_q_op < 600 or tia_q_op > 720 or tia_q_on < 600 or tia_q_on > 720)
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
            break
        # rx off
        uart0.write_reg_mask("40344088", "20:19", 2)
        time.sleep(0.01)
        print('Pass %d' % i)
    return flag_error


if __name__ == "__main__":
    comport = 14
    uart0 = uart_open(comport)
    adc = MSADC()

    uart0.write_reg_mask("40344088", "17:14", 12)
    flag_x = 0
    for xi in range(15):
        uart0.write_reg_mask("40344088", "13:10", xi)
        uart0.write_reg_mask("40344088", "18", 1)
        flag_x = test_tia_dc()
        if flag_x == 1:
            print('Fail @ AGC: %d' % xi)
            print('Bad Die!')
            break
    if flag_x == 0:
        print('Finish the fast scan')
        for xi in range(15):
            uart0.write_reg_mask("40344088", "13:10", xi)
            uart0.write_reg_mask("40344088", "18", 1)
            flag_x = scan_tia_dc()
            if flag_x == 1:
                print('Fail @ AGC: %d' % xi)
                print('Bad Die!')
                break
    if flag_x == 0:
        print('Pass All AGC Gears ^_^')
        print('Good Die!')

    uart_close()