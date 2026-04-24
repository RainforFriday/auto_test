import os
import sys
import time
import numpy

from aic8822.msadc.msadc import bt_pa_on, msadc_rfdc_init, msadc_ms
from aic8822.pwr_sense.pwr_sense import pa_pwrsense_lb0_on, pa_pwrsense_lb0_off, pa_pwrsense_hb0_on, pa_pwrsense_hb0_off
from aicintf.uart import *
from aicintf.com import *
from aicbasic.AIC_C_CODE_LOG import *
from aicinstr.rs.fsq import *
import msadc
import pwr_sense

def fsq_init(fsqx):
    fsqx.set_analyzer_mode()
    fsqx.set_span(50)
    fsqx.set_rb(1)
    fsqx.set_reflvl(30)
    fsqx.set_cfreq(2442)
    time.sleep(1)

def CSV_MCS(csv_name, INDEX, DATA_LIST):
    with open(csv_name, "a+") as  CSVFILE:
        CSVFILE.write(INDEX + "," +",".join(DATA_LIST) + "\n")


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc


def uart_close():
    UARTc.close()

def mea_pwr_ant0(UARTc):
    for i in range(64,int(0xfff)+1,32):
        print("tone_on 01 1 "+str(hex(i)[2:])+" c")
        UARTc.sendcmd("tone_on 01 1 "+str(hex(i)[2:])+" c")
        time.sleep(0.5)
        freq = round(float(fsqx.get_peak_mark()[0])/1000000,2)
        pwr=round(float(fsqx.get_peak_mark()[1]),2)
        pwr_s = msadc_ms(UARTc)
        date=str(hex(i)[2:])+","+str(i)+","+str(freq)+","+str(pwr)+","+str(pwr_s)
        with open("./" + csv_name, "a+", ) as  CSVFILE:
            CSVFILE.write(BOR+ "," +date+"\n")
        print(freq)
        print(pwr)
        print(pwr_s)

def mea_pwr_ant1(UARTc):
    for i in range(64,int(str(0xfff),16)+1,32):
        print("tone_on 10 1 "+str(hex(i)[2:])+" c")
        UARTc.sendcmd("tone_on 10 1 "+str(hex(i)[2:])+" c")
        time.sleep(0.5)
        freq = round(float(fsqx.get_peak_mark()[0])/1000000,2)
        pwr=round(float(fsqx.get_peak_mark()[1]),2)
        pwr_s = msadc_ms(UARTc)
        date=str(hex(i)[2:])+","+str(i)+","+str(freq)+","+str(pwr)+","+str(pwr_s)
        with open("./" + csv_name, "a+", ) as  CSVFILE:
            CSVFILE.write(BOR+ "," +date+"\n")
        print(freq)
        print(pwr)
        print(pwr_s)

if __name__ == "__main__":
    global UARTc
    comport = 8
    uart_open(comport)
    FSQ_IP = "10.21.10.154"
    fsqx = FSQ()
    fsqx.open_tcp(FSQ_IP)
    print(fsqx.id_string())
    fsq_init(fsqx)
    BOR="NO4"
    csv_name="aic8822_pwrsense_test_1.csv"
    CH=[100]
    bt_pa_on(UARTc)
    msadc_rfdc_init(UARTc)
    ant0=True
    ant1=False

    if ant0==True:
        for ch in CH:
            UARTc.sendcmd("setch "+str(ch))
            if ch<20:
                fsqx.set_cfreq((ch-1)*5+2412)
                pa_pwrsense_lb0_on(UARTc)
                mea_pwr_ant0(UARTc)
                pa_pwrsense_lb0_off(UARTc)
            else:
                fsqx.set_cfreq((ch-36)*5+5180)
                pa_pwrsense_hb0_on(UARTc)
                mea_pwr_ant0(UARTc)
                pa_pwrsense_hb0_off(UARTc)
            UARTc.sendcmd("tone_off")

    if ant1==True:
        for ch in CH:
            UARTc.sendcmd("setch "+str(ch))
            if ch<20:
                fsqx.set_cfreq((ch - 1) * 5 + 2412)
                fsqx.set_cfreq(2442)
                pa_pwrsense_lb0_on(UARTc)
                mea_pwr_ant1(UARTc)
                pa_pwrsense_lb0_off(UARTc)
            else:
                fsqx.set_cfreq((ch-36)*5+5180)
                pa_pwrsense_hb0_on(UARTc)
                mea_pwr_ant1(UARTc)
                pa_pwrsense_hb0_off(UARTc)
            UARTc.sendcmd("tone_off")

    fsqx.close()
    UARTc.close()