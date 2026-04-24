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

comport = 8
uart0 = uart_open(comport)
adc = MSADC()

# measure
#uart0.write_reg_mask("4034400C", "24", 1)  # turn on test_enable_dtmx
#uart0.write_reg_mask("40344008", ["2:0"], [0])  # set wf_test_bit dvdd
dtmx_dvdd = adc.ms_portdc()


print('dtmx_dvdd : %.1f  mV' % dtmx_dvdd)


uart_close()