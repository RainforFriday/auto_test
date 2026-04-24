import os
from icbasic.aicintf.uart import *

def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()


def pa_pwrsense_lb0_on(UARTc):
    # loft en
    UARTc.write_reg_mask("403440A8", "20", 1)
    # loft vi mode
    UARTc.write_reg_mask("403440A8", "14", 1)
    # loft lpf mode
    UARTc.write_reg_mask("403440A8", "15", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440A8", "13:11", 4)
    # test_enable lb0 pa
    UARTc.write_reg_mask("40344024", "18", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)



def pa_pwrsense_lb0_off(UARTc):
    # loft en
    UARTc.write_reg_mask("403440A8", "20", 0)
    # loft vi mode
    UARTc.write_reg_mask("403440A8", "14", 0)
    # loft lpf mode
    UARTc.write_reg_mask("403440A8", "15", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440A8", "13:11", 4)
    # test_enable lb0 pa
    UARTc.write_reg_mask("40344024", "18", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)



def pa_pwrsense_hb0_on(UARTc):
    # loft en
    UARTc.write_reg_mask("40344070", "14", 1)
    # loft vi mode
    UARTc.write_reg_mask("40344070", "8", 1)
    # loft lpf mode
    UARTc.write_reg_mask("40344070", "9", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344070", "7:5", 4)
    # test_enable hb0 pa
    UARTc.write_reg_mask("40344024", "26", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)



def pa_pwrsense_hb0_off(UARTc):
    # loft en
    UARTc.write_reg_mask("40344070", "14", 0)
    # loft vi mode
    UARTc.write_reg_mask("40344070", "8", 0)
    # loft lpf mode
    UARTc.write_reg_mask("40344070", "9", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344070", "7:5", 4)
    # test_enable hb0 pa
    UARTc.write_reg_mask("40344024", "26", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)



def pa_pwrsense_lb1_on(UARTc):
    # loft en
    UARTc.write_reg_mask("40344118", "19", 1)
    # loft vi mode
    UARTc.write_reg_mask("40344118", "13", 1)
    # loft lpf mode
    UARTc.write_reg_mask("40344118", "14", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344118", "12:10", 4)
    # test_enable lb1 pa
    UARTc.write_reg_mask("40344024", "1", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)



def pa_pwrsense_lb1_off(UARTc):
    # loft en
    UARTc.write_reg_mask("40344118", "19", 0)
    # loft vi mode
    UARTc.write_reg_mask("40344118", "13", 0)
    # loft lpf mode
    UARTc.write_reg_mask("40344118", "14", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("40344118", "12:10", 4)
    # test_enable lb1 pa
    UARTc.write_reg_mask("40344024", "1", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)



def pa_pwrsense_hb1_on(UARTc):
    # loft en
    UARTc.write_reg_mask("403440E4", "22", 1)
    # loft vi mode
    UARTc.write_reg_mask("403440E4", "16", 1)
    # loft lpf mode
    UARTc.write_reg_mask("403440E4", "17", 1)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440E4", "15:13", 4)
    # test_enable hb1 pa
    UARTc.write_reg_mask("40344024", "9", 1)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 3)



def pa_pwrsense_hb1_off():
    # loft en
    UARTc.write_reg_mask("403440E4", "22", 0)
    # loft vi mode
    UARTc.write_reg_mask("403440E4", "16", 0)
    # loft lpf mode
    UARTc.write_reg_mask("403440E4", "17", 0)
    # loft mixer bias bit
    UARTc.write_reg_mask("403440E4", "15:13", 4)
    # test_enable hb1 pa
    UARTc.write_reg_mask("40344024", "9", 0)
    # test bit
    UARTc.write_reg_mask("40502018", "17:15", 0)
    # mode bit
    UARTc.write_reg_mask("40502018", "8:7", 0)