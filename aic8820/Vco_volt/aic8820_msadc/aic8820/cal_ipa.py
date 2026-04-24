# @20230423
# for U03
# @20230517 add cal_i_pa24g/i_pa24g/m_i_pa24g
import os
import sys
from msadc import *
from aicbasic.AIC_C_CODE_LOG import *


def cal_i_pa5g(i_target_mA = 120.0):
    global MSADCx
    MSADCx = MSADC()

    # 1 msadc inital
    wlog("// adc basiconfig")
    MSADCx.basiconfig()

    # 2 adc config
    wlog("//adc config")
    MSADCx.adconfig()

    # 3 msadc input sel pa sense
    MSADCx.input_sel_isense()

    # 4 isense sel pacore
    MSADCx.pa5g_cal_selcore()

    # 5 set apc and index
    cal_i_pa5g_sel_apc_mcs11_index_c()

    # 6 tx on
    reg_txon_init = UARTc.read_reg_bits("40344088", "22:19")   # get_txon init value
    UARTc.write_reg_mask("40344088", "22:19", 14)  # set tx always on, rx always off

    # 7 calibration pa current
    pa5g_cal_res_value_init = 4
    pa5g_cal_cgm_value_init = 8
    ## vl1 res
    UARTc.write_reg_mask("40344030", "2:0", pa5g_cal_res_value_init)
    ## vl2 res
    UARTc.write_reg_mask("40344034", "14:12", pa5g_cal_res_value_init)
    ## vl1 cgm
    UARTc.write_reg_mask("40344030","6:3", pa5g_cal_cgm_value_init)
    ## vl2 cgm
    UARTc.write_reg_mask("40344034","18:15", pa5g_cal_cgm_value_init)

    # measure pa current
    i_pa0 = i_pa5g()
    if i_pa0 < i_target_mA:
        cal_sign = 1
    elif i_pa0 > i_target_mA:
        cal_sign = -1
    else:
        cal_sign = 0

    i_pa_ref = i_pa0

    cal_offset_result = 0
    i_pa_result = i_pa_ref

    pa5g_cal_res_value_ref = pa5g_cal_res_value_init
    pa5g_cal_cgm_value_ref = pa5g_cal_cgm_value_init
    for i in range(7):
        if cal_sign == 0:
            i_pa_result = i_pa_ref
            break

        ## cal offset
        cal_offset_result = cal_offset_result + cal_sign

        # print("cal_offset_results: " + str(cal_offset_result))

        ## res value
        if pa5g_cal_res_value_init + cal_offset_result > 7:
            pa5g_cal_res_value = 7
        elif pa5g_cal_res_value_init + cal_offset_result < 0:
            pa5g_cal_res_value = 0
        else:
            pa5g_cal_res_value = pa5g_cal_res_value_init + cal_offset_result

        ## cgm value
        pa5g_cal_cgm_value = pa5g_cal_cgm_value_init + pa5g_cal_res_value_init + cal_offset_result - pa5g_cal_res_value

        if pa5g_cal_cgm_value > 15:
            pa5g_cal_cgm_value = 15
        elif pa5g_cal_cgm_value < 0:
            pa5g_cal_cgm_value = 0
        else:
            pa5g_cal_cgm_value = pa5g_cal_cgm_value

        ## pa 5g vl1 res
        UARTc.write_reg_mask("40344030", "2:0", pa5g_cal_res_value)
        ## pa 5g vl2 res
        UARTc.write_reg_mask("40344034", "14:12", pa5g_cal_res_value)
        ## pa 5g vl1 cgm
        UARTc.write_reg_mask("40344030","6:3", pa5g_cal_cgm_value)
        ## pa 5g vl2 cgm
        UARTc.write_reg_mask("40344034","18:15", pa5g_cal_cgm_value)


        ## measure current of pa
        i_pax = i_pa5g()

        print("{}/{}: {}".format(pa5g_cal_res_value, pa5g_cal_cgm_value, i_pax))

        ##
        if (i_pax - i_target_mA)*(i_pa_ref - i_target_mA) <= 0:
            if abs(i_pax - i_target_mA) < abs(i_pa_ref - i_target_mA):
                i_pa_result = i_pax
            else:
                pa5g_cal_res_value = pa5g_cal_res_value_ref
                pa5g_cal_cgm_value = pa5g_cal_cgm_value_ref
                i_pa_result = i_pa_ref
                # write calibration results
                UARTc.write_reg_mask("40344030", "2:0", pa5g_cal_res_value)
                UARTc.write_reg_mask("40344034", "14:12", pa5g_cal_res_value)
                UARTc.write_reg_mask("40344030","6:3", pa5g_cal_cgm_value)
                UARTc.write_reg_mask("40344034","18:15", pa5g_cal_cgm_value)
            break
        else:
            i_pa_ref = i_pax
        
        pa5g_cal_res_value_ref = pa5g_cal_res_value
        pa5g_cal_cgm_value_ref = pa5g_cal_cgm_value


    # 8 turn off pa cal
    MSADCx.pa5g_cal_off()

    # 9 recovery tx man ctrl
    UARTc.write_reg_mask("40344088", "22:19", reg_txon_init)  # set tx always on, rx always off

    # 10 calibration off
    return i_pa0, pa5g_cal_res_value, pa5g_cal_cgm_value, i_pa_result


def cal_i_pa24g(i_target_mA = 100.0):
    global MSADCx
    MSADCx = MSADC()

    # 1 msadc inital
    wlog("// adc basiconfig")
    MSADCx.basiconfig()

    # 2 adc config
    wlog("//adc config")
    MSADCx.adconfig()

    # 3 msadc input sel pa sense
    MSADCx.input_sel_isense()

    # 4 isense sel pacore
    MSADCx.pa24g_cal_selcore()

    # 5 set apc and index
    cal_i_pa24g_sel_apc_mcs11_index_b()

    # 6 tx on
    reg_txon_init = UARTc.read_reg_bits("40344088", "22:19")   # get_txon init value
    UARTc.write_reg_mask("40344088", "22:19", 14)  # set tx always on, rx always off

    # 7 calibration pa current
    pa24g_cal_reg_value_init = 4
    UARTc.write_reg_mask("40344038", "28:26", pa24g_cal_reg_value_init)
    
    cal_offset = 0

    # measure pa current
    i_pa0 = i_pa24g()
    if i_pa0 < i_target_mA:
        cal_sign = 1
    elif i_pa0 > i_target_mA:
        cal_sign = -1
    else:
        cal_sign = 0

    i_pa_ref = i_pa0
    pa24g_cal_reg_value = pa24g_cal_reg_value_init
    cal_offset_result = 0
    i_pa_result = i_pa_ref
    for i in range(4):
        if cal_sign == 0:
            cal_offset_result = 0
            i_pa_result = i_pa_ref
            break

        ## write cal value
        cal_offset_result = cal_offset_result + cal_sign
        pa24g_cal_reg_value = pa24g_cal_reg_value + cal_sign

        if pa24g_cal_reg_value > 7:
            pa24g_cal_reg_value = 7
            cal_offset_result = pa24g_cal_reg_value - pa24g_cal_reg_value_init
        if pa24g_cal_reg_value < 0:
            pa24g_cal_reg_value = 0
            cal_offset_result = pa24g_cal_reg_value - pa24g_cal_reg_value_init

        ## pa 24g vl resbit
        UARTc.write_reg_mask("40344038", "28:26", pa24g_cal_reg_value)

        ## measure current of pa
        i_pax = i_pa24g()

        print("{}: {}".format(pa24g_cal_reg_value, i_pax))

        ##
        if (i_pax - i_target_mA)*(i_pa_ref - i_target_mA) <= 0:
            if abs(i_pax - i_target_mA) < abs(i_pa_ref - i_target_mA):
                cal_offset_result = cal_offset_result
                i_pa_result = i_pax
            else:
                cal_offset_result = cal_offset_result - cal_sign
                i_pa_result = i_pa_ref
                ### write calibration results
                UARTc.write_reg_mask("40344038", "28:26", cal_offset_result + pa24g_cal_reg_value_init)
            break
        else:
            i_pa_ref = i_pax



    # 8 turn off pa cal
    MSADCx.pa24g_cal_off()

    # 9 recovery tx man ctrl
    UARTc.write_reg_mask("40344088", "22:19", reg_txon_init)  # set tx always on, rx always off

    # 10 calibration off
    return i_pa0, cal_offset_result, i_pa_result


def cal_i_pa5g_sel_apc_mcs11_index_c():
    UARTc.sendcmd("settx 0")
    # load mcs11 table
    UARTc.sendcmd("setch 122")
    UARTc.sendcmd("setrate 5 11")

    # select pwr index
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd("setpwr 16")

    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")



def cal_i_pa24g_sel_apc_mcs11_index_b():
    UARTc.sendcmd("settx 0")
    # load mcs11 table
    UARTc.sendcmd("setch 7")
    UARTc.sendcmd("setrate 5 11")

    # select pwr index
    UARTc.sendcmd("pwrmm 1")
    UARTc.sendcmd("setpwr 18")

    UARTc.sendcmd("settx 1")
    UARTc.sendcmd("settx 0")



def i_pa5g():
    # pa1_en , apc wf_pa_5g_vl_en_bit = 2'b01
    UARTc.sendcmd("setapc 35 34 1")
    v_pa1 = MSADCx.ms_volt()
    #print("v_pa1: " + str(v_pa1))

    # pa2_en , apc wf_pa_5g_vl_en_bit = 2'b10
    UARTc.sendcmd("setapc 35 34 2")
    # time.sleep(1)
    v_pa2 = MSADCx.ms_volt()
    #print("v_pa2: " + str(v_pa2))

    # get i_pa
    i_pa = (v_pa1/1.552 * 8.0 + v_pa2/1.552 * 6.0) * 32.0 * 1.06
    #print("PA CURRENT : " + str(i_pa) + "mA")

    # apc recover
    UARTc.sendcmd("setapc 35 34 3")
    return i_pa


def i_pa24g():
    #measure ipa
    v_pa = MSADCx.ms_volt()
    # get i_pa
    i_pa = (v_pa/1.552 * 16.0) * 32.0 * 1.06
    return i_pa


def m_i_pa5g(reg_value = 8):
    global MSADCx
    MSADCx = MSADC()

    # 1 msadc inital
    wlog("// adc basiconfig")
    MSADCx.basiconfig()

    # 2 adc config
    wlog("//adc config")
    MSADCx.adconfig()

    # 3 msadc input sel pa sense
    MSADCx.input_sel_isense()

    # 4 isense sel pacore
    MSADCx.pa5g_cal_selcore()

    # 5 set apc and index
    cal_i_pa5g_sel_apc_mcs11_index_c()

    # 6 tx on
    reg_txon_init = UARTc.read_reg_bits("40344088", "22:19")   # get_txon init value
    UARTc.write_reg_mask("40344088", "22:19", 14)  # set tx always on, rx always off

    # 7 write reg
    UARTc.write_reg_mask("40344030", "2:0", reg_value)
    UARTc.write_reg_mask("40344034", "14:12", reg_value)

    # 8 measure current of pa
    i_pax = i_pa5g()

    # 9 turn off pa cal
    MSADCx.pa5g_cal_off()

    # 10 recovery tx man ctrl
    UARTc.write_reg_mask("40344088", "22:19", reg_txon_init)  # set tx always on, rx always off

    return i_pax


def m_i_pa24g(reg_value = 8):
    global MSADCx
    MSADCx = MSADC()

    # 1 msadc inital
    wlog("// adc basiconfig")
    MSADCx.basiconfig()

    # 2 adc config
    wlog("//adc config")
    MSADCx.adconfig()

    # 3 msadc input sel pa sense
    MSADCx.input_sel_isense()

    # 4 isense sel pacore
    MSADCx.pa24g_cal_selcore()

    # 5 set apc and index
    cal_i_pa24g_sel_apc_mcs11_index_b()

    # 6 tx on
    reg_txon_init = UARTc.read_reg_bits("40344088", "22:19")   # get_txon init value
    UARTc.write_reg_mask("40344088", "22:19", 14)  # set tx always on, rx always off

    # 7 write reg wf_pa24g_vl_rfdyn_vrthbit
    UARTc.write_reg_mask("40344038", "28:26", reg_value)

    # 8 measure current of pa
    i_pax = i_pa24g()

    # 9 turn off pa cal
    MSADCx.pa24g_cal_off()

    # 10 recovery tx man ctrl
    UARTc.write_reg_mask("40344088", "22:19", reg_txon_init)  # set tx always on, rx always off

    return i_pax


if __name__ == "__main__":

    #AIC_C_CODE_LOG(True)
    #global logf
    global UARTc
    COM_NUM = 8

    UARTc = uart_open(COM_NUM)

    """
    reg_init = 4
    i_pa0, cal_offset_result, i_pa_result = cal_i_pa5g(120)
    print("{}:{}, {}:{}".format(reg_init, i_pa0, reg_init+cal_offset_result, i_pa_result))
    """


    i_pa0, res_value, cgm_value, i_pa_result = cal_i_pa5g(150)
    print("default Current:{}, After Calibration: {}/{} -> {}".format(i_pa0, res_value, cgm_value, i_pa_result))


    #reg = 3
    #current = m_i_pa5g(reg)
    #print("reg: {}, current: {}".format(reg, current))

    """
    for reg in range(8):
        current = m_i_pa24g(reg)
        print("reg: {}, current: {}".format(reg, current))
    """

    uart_close()