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

comport = 6
uart0 = uart_open(comport)
adc = MSADC()

# measure
uart0.write_reg_mask("4034400C", ["27:26"], [1])  # turn on test_enable_tia
uart0.write_reg_mask("40344008", ["2:0"], [3])  # set wf_test_bit
tia_vreg = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [4])  # set wf_test_bit
tia_i_ip = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [5])  # set wf_test_bit
tia_i_in = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [6])  # set wf_test_bit
tia_q_ip = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [7])  # set wf_test_bit
tia_q_in = adc.ms_portdc()
uart0.write_reg_mask("4034400C", ["27:26"], [2])  # turn off test_enable_tia
uart0.write_reg_mask("40344008", ["2:0"], [4])  # set wf_test_bit
tia_i_op = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [5])  # set wf_test_bit
tia_i_on = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [6])  # set wf_test_bit
tia_q_op = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [7])  # set wf_test_bit
tia_q_on = adc.ms_portdc()
uart0.write_reg_mask("4034400C", ["27:26"], [0])  # turn off test_enable_tia
uart0.write_reg_mask("4034400C", ["19"],  [1])  # turn off test_enable_tia
uart0.write_reg_mask("40344008", ["2:0"], [0])  # set wf_test_bit
adc_dvdd = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [1])  # set wf_test_bit
adc_vref = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [2])  # set wf_test_bit
adc_vcm = adc.ms_portdc()
uart0.write_reg_mask("40344008", ["2:0"], [3])  # set wf_test_bit
adc_vss = adc.ms_portdc()

print('tia_vreg : %.1f  mV' % tia_vreg)
print('tia_i_ip : %.1f  mV' % tia_i_ip)
print('tia_i_in : %.1f  mV' % tia_i_in)
print('tia_q_ip : %.1f  mV' % tia_q_ip)
print('tia_q_in : %.1f  mV' % tia_q_in)
print('tia_i_op : %.1f  mV' % tia_i_op)
print('tia_i_on : %.1f  mV' % tia_i_on)
print('tia_q_op : %.1f  mV' % tia_q_op)
print('tia_q_on : %.1f  mV' % tia_q_on)
print('adc_dvdd : %.1f  mV' % adc_dvdd)
print('adc_vreg : %.1f  mV' % adc_vref)
print('adc_vcm  : %.1f  mV' % adc_vcm)
print('adc_vss  : %.1f  mV' % adc_vss)

uart_close()