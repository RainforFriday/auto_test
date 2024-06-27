# @20230423
# for U03
# @20230517 add cal_i_pa24g/i_pa24g/m_i_pa24g
import os
import sys
from msadc import *
from aicbasic.AIC_C_CODE_LOG import *

global UARTc


def pu_bt_pa():
    UARTc.write_reg_mask("40622000", "3:2", 3)   #pu bt_pa


def cal_i_tx_hb0(i_pa_mA = 120.0, i_padrv_mA = 40.0):
    pass


def i_ms_tx_hb0():
    # step0: ms adc init
    msadc_dcinit()

    # step1: pa/padrv power up
    # trxsw hb0 dr on
    UARTc.write_reg_mask("40344000", "17:16", 3)
    # pa on
    UARTc.write_reg_mask("40344000", "19:18", 3)
    # padrv on
    UARTc.write_reg_mask("40344000", "21:20", 3)

    # step2: isense en
    UARTc.write_reg_mask("40344070", "21", 1)      #isense_en
    UARTc.write_reg_mask("40344070", "20:18", 4)   #isense_rbit =4

    # step3: test_enable on
    UARTc.write_reg_mask("40344024", "26", 1)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 3)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 2)   # pa test bit

    # step4: measure isense offset
    UARTc.write_reg_mask("40344000", "15:14", 2)   # pa gain dr 0
    UARTc.write_reg_mask("40344070", "16:15", 2)   # isense sel pa on, padrv off
    v_isense_offset = msadc_ms()
    print("offset voltage : " + str(v_isense_offset))

    # step5: measure pa current
    UARTc.write_reg_mask("40344000", "15:14", 3)   # pa gain dr 1
    pa_v_vlaue = msadc_ms()
    pa_res_hb0 = 0.354
    i_pa = (pa_v_vlaue - v_isense_offset)/pa_res_hb0
    print("measure voltage : " + str(pa_v_vlaue))
    print("measure current : " + str(i_pa))
    UARTc.write_reg_mask("40344000", "15:14", 0)   # pa gain dr release

    # step6: measure padrv current
    UARTc.write_reg_mask("40344070", "16:15", 1)   # isense sel pa off, padrv on
    UARTc.write_reg_mask("40344060", "18", 1)      # isense padrv sel pa
    padrv_v_vlaue = msadc_ms()
    padrv_res_hb0 = 2.09
    i_padrv = (padrv_v_vlaue - v_isense_offset)/padrv_res_hb0
    print("measure voltage : " + str(padrv_v_vlaue))
    print("measure current : " + str(i_padrv))

    # step7: close
    UARTc.write_reg_mask("40344000", "15:14", 0)   # pa gain dr release
    UARTc.write_reg_mask("40344024", "26", 0)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 0)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 0)   # pa test bit
    UARTc.write_reg_mask("40344070", "21", 0)      #isense_en
    UARTc.write_reg_mask("40344070", "20:18", 0)   #isense_rbit =4
    UARTc.write_reg_mask("40344070", "16:15", 2)   #isense sel pa off, padrv off
    UARTc.write_reg_mask("40344000", "21:20", 0)   #padrv off
    UARTc.write_reg_mask("40344000", "19:18", 0)   #pa off
    UARTc.write_reg_mask("40344000", "17:16", 0)   #trxsw off

    return i_pa


def i_ms_tx_lb0():
    # step0: ms adc init
    msadc_dcinit()

    # step1: pa/padrv power up
    # trxsw lb0 dr on
    UARTc.write_reg_mask("40344004", "15:14", 3)
    # pa on
    UARTc.write_reg_mask("40344004", "17:16", 3)
    # padrv on
    UARTc.write_reg_mask("40344004", "23:22", 3)

    # step2: isense en
    UARTc.write_reg_mask("403440A4", "5", 1)      #isense_en
    UARTc.write_reg_mask("403440A4", "4:2", 4)   #isense_rbit =4

    # step3: test_enable on
    UARTc.write_reg_mask("40344024", "18", 1)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 3)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 1)   # pa test bit

    # step4: measure isense offset
    UARTc.write_reg_mask("40344004", "13:12", 2)   # pa gain dr 0
    UARTc.write_reg_mask("403440A4", "0", 1)   # isense sel pa on
    UARTc.write_reg_mask("403440A8", "21", 0)   # isense sel padrv off
    v_isense_offset = msadc_ms()
    print("offset voltage : " + str(v_isense_offset))

    # step5: measure pa current
    UARTc.write_reg_mask("40344004", "13:12", 3)   # pa gain dr 1
    pa_v_vlaue = msadc_ms()
    pa_res_hb0 = 0.354
    i_pa = (pa_v_vlaue - v_isense_offset)/pa_res_hb0
    print("measure voltage : " + str(pa_v_vlaue))
    print("measure current : " + str(i_pa))
    UARTc.write_reg_mask("40344004", "13:12", 0)   # pa gain dr release

    # step6: measure padrv current
    UARTc.write_reg_mask("403440A4", "0", 0)   # isense sel pa off
    UARTc.write_reg_mask("403440A8", "21", 1)   # isense sel padrv on
    UARTc.write_reg_mask("40344098", "27", 1)      # isense sel padrv p1
    padrv_v_vlaue = msadc_ms()
    padrv_res_hb0 = 0.354
    i_padrv = (padrv_v_vlaue - v_isense_offset)/padrv_res_hb0
    print("measure voltage : " + str(padrv_v_vlaue))
    print("measure current : " + str(i_padrv))

    # step7: close
    UARTc.write_reg_mask("40344004", "13:12", 0)   # pa gain dr release
    UARTc.write_reg_mask("40344024", "18", 0)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 0)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 0)   # pa test bit
    UARTc.write_reg_mask("403440A4", "5", 0)      #isense_en
    UARTc.write_reg_mask("403440A4", "4:2", 0)   #isense_rbit =4
    UARTc.write_reg_mask("403440A4", "0", 0)   # isense sel pa on
    UARTc.write_reg_mask("403440A8", "21", 0)   # isense sel padrv on
    UARTc.write_reg_mask("40344004", "23:22", 0)   # padrv dr release
    UARTc.write_reg_mask("40344004", "17:16", 0)   # pa dr release
    UARTc.write_reg_mask("40344004", "15:14", 0)   # trxsw off

    return i_pa


def i_ms_tx_hb1():
    # step0: ms adc init
    msadc_dcinit()

    # step1: pa/padrv power up
    # trxsw hb1 dr on
    UARTc.write_reg_mask("40344008", "11:10", 3)
    # pa on
    UARTc.write_reg_mask("40344008", "13:12", 3)
    # padrv on
    UARTc.write_reg_mask("40344008", "15:14", 3)

    # step2: isense en
    UARTc.write_reg_mask("403440E0", "3", 1)      #isense_en
    UARTc.write_reg_mask("403440E0", "2:0", 4)   #isense_rbit =4

    # step3: test_enable on
    UARTc.write_reg_mask("40344024", "9", 1)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 3)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 2)   # pa test bit

    # step4: measure isense offset
    UARTc.write_reg_mask("40344008", "9:8", 2)   # pa gain dr 0
    UARTc.write_reg_mask("403440E4", "24:23", 2)   # isense sel pa on, padrv off
    v_isense_offset = msadc_ms()
    print("offset voltage : " + str(v_isense_offset))

    # step5: measure pa current
    UARTc.write_reg_mask("40344008", "9:8", 3)   # pa gain dr 1
    pa_v_vlaue = msadc_ms()
    pa_res_hb0 = 0.354
    i_pa = (pa_v_vlaue - v_isense_offset)/pa_res_hb0
    print("measure voltage : " + str(pa_v_vlaue))
    print("measure current : " + str(i_pa))
    UARTc.write_reg_mask("40344008", "9:8", 0)   # pa gain dr release

    # step6: measure padrv current
    UARTc.write_reg_mask("403440E4", "24:23", 1)   # isense sel pa off, padrv on
    UARTc.write_reg_mask("403440D0", "0", 1)      # isense padrv sel p1
    padrv_v_vlaue = msadc_ms()
    padrv_res_hb0 = 0.354
    i_padrv = (padrv_v_vlaue - v_isense_offset)/padrv_res_hb0
    print("measure voltage : " + str(padrv_v_vlaue))
    print("measure current : " + str(i_padrv))

    # step7: close
    UARTc.write_reg_mask("40344008", "9:8", 0)   # pa gain dr release
    UARTc.write_reg_mask("40344024", "9", 0)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 0)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 0)   # pa test bit
    UARTc.write_reg_mask("403440E0", "3", 0)      #isense_en
    UARTc.write_reg_mask("403440E0", "2:0", 0)   #isense_rbit =0
    UARTc.write_reg_mask("403440E4", "24:23", 0)   # isense sel pa off, padrv on
    UARTc.write_reg_mask("40344008", "15:14", 3)   # padrv dr release
    UARTc.write_reg_mask("40344008", "13:12", 3)   # pa dr release
    UARTc.write_reg_mask("40344008", "11:10", 3)   # trxsw dr release

    return i_pa


def i_ms_tx_lb1():
    # step0: ms adc init
    msadc_dcinit()

    # step1: pa/padrv power up
    # trxsw lb1 dr on
    UARTc.write_reg_mask("4034400C", "11:10", 3)
    # pa on
    UARTc.write_reg_mask("4034400C", "13:12", 3)
    # padrv on
    UARTc.write_reg_mask("4034400C", "17:16", 3)

    # step2: isense en
    UARTc.write_reg_mask("40344114", "5", 1)      #isense_en
    UARTc.write_reg_mask("40344114", "4:2", 4)   #isense_rbit =4

    # step3: test_enable on
    UARTc.write_reg_mask("40344024", "1", 1)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 3)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 2)   # pa test bit

    # step4: measure isense offset
    UARTc.write_reg_mask("4034400C", "9:8", 2)   # pa gain dr 0
    UARTc.write_reg_mask("40344114", "0", 1)   # isense sel pa on
    UARTc.write_reg_mask("40344118", "20", 0)   # isense sel padrv off
    v_isense_offset = msadc_ms()
    print("offset voltage : " + str(v_isense_offset))

    # step5: measure pa current
    UARTc.write_reg_mask("4034400C", "9:8", 3)   # pa gain dr 1
    pa_v_vlaue = msadc_ms()
    pa_res_hb0 = 0.354
    i_pa = (pa_v_vlaue - v_isense_offset)/pa_res_hb0
    print("measure voltage : " + str(pa_v_vlaue))
    print("measure current : " + str(i_pa))
    UARTc.write_reg_mask("4034400C", "9:8", 0)   # pa gain dr release

    # step6: measure padrv current
    UARTc.write_reg_mask("40344114", "0", 0)  # isense sel pa off
    UARTc.write_reg_mask("40344118", "20", 1)  # isense sel padrv on
    UARTc.write_reg_mask("40344108", "24", 1)  # isense sel padrv p1

    padrv_v_vlaue = msadc_ms()
    padrv_res_hb0 = 0.354
    i_padrv = (padrv_v_vlaue - v_isense_offset)/padrv_res_hb0
    print("measure voltage : " + str(padrv_v_vlaue))
    print("measure current : " + str(i_padrv))

    # step7: close
    UARTc.write_reg_mask("4034400C", "9:8", 0)   # pa gain dr release
    UARTc.write_reg_mask("40344024", "1", 0)      # pa test enable
    UARTc.write_reg_mask("40502018", "8:7", 0)     # pa test mode
    UARTc.write_reg_mask("40502018", "17:15", 0)   # pa test bit
    UARTc.write_reg_mask("40344114", "5", 0)      #isense_en
    UARTc.write_reg_mask("40344114", "4:2", 0)   #isense_rbit =4
    UARTc.write_reg_mask("40344114", "0", 0)  # isense sel pa off
    UARTc.write_reg_mask("40344118", "20", 0)  # isense sel padrv off
    UARTc.write_reg_mask("4034400C", "17:16", 0)  # padrv dr release
    UARTc.write_reg_mask("4034400C", "13:12", 0)  # pa dr release
    UARTc.write_reg_mask("4034400C", "11:10", 0)  # trxsw dr release

    return i_pa



if __name__ == "__main__":
    global UARTc
    COM_NUM = 20
    UARTc = uart_open(COM_NUM)
    pu_bt_pa()
    i_ms_tx_hb0()
    #i_ms_tx_lb0()
    # print("i_pa = " + str(i_pa) + "mA!!!")
