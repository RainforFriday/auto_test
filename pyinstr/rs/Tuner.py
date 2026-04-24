# encoding: utf-8
"""
@version: 0-0
@author: yudunyang
@site:
@software: PyCharm
@file:Tuner.py
@time: 2022/7/14 14：29
"""

import os
import sys
import pyvisa as visa
from pyintf.uart import *
from pyinstr.rs.cmw import *
from pyinstr.rs.genericinstrument import *
from pyintf.uart import *
import csv
import pandas as pd

__version__ = "v0.1"


class tuner(Uart):
    def __init__(self):
        super(tuner,self).__init__()
        # self.freq = ["2412", "2442","2472","5180","5300","5500","5650","5745","5785","5825","6200","6475","6700","7000"]
        self.freq = ["2412", "2442","2472","5180","5300","5500","5745","5785","5800","5825","6200","6475","6700","7000"]

    def open(self,UART1):
        return print(UART1.sendcmd("*IDN?\n"))

    def reset(self,UART1):
        UART1.sendcmd("*RST; *OPC?")
        return True

    def clear(self,UART1):
        UART1.sendcmd("*CLS; *OPC?")
        return True

    def read(self,UART1):
        UART1.sendcmd("dir?")
        return True

    def load_file(self, UART1, FRE="2412"):
        if FRE not in self.freq:
            print("Set Frequence Error, Abort!!!")
            sys.exit(0)
        else:
            UART1.sendcmd("calib {}".format(str(FRE))+"M.tun\n")
            UART1.sendcmd("freq {}".format(int(FRE)/1000)+"\n")
        return True

    def set_tune(self,UART1,ampt=0,unphase=90, max_retries=3):
        for attempt in range(max_retries):
            UART1.sendcmd("tune {}".format(ampt)+" {}\n".format(unphase))
            time.sleep(2)
            A=self.query_gamma(UART1)
            print(A)
            # B=self.query_postion(UART1)
            if A and A.strip():  # 非空且非纯空白字符
                break  # 有效数据，退出循环
            print(f"第 {attempt + 1} 次尝试失败，返回空值")
            time.sleep(2)
        else:
            raise ValueError(f"Tune  {max_retries} times return null")
        #print(A)
        #print(B)
        #print(A)
        #print(A.split(",")[1])
        #print(self.query_gamma(UART1).split(",")[2])
        count=0
        # print(A)
        # print(B)
        while True:
            phase_flag = (abs(float(A.split(",")[2])) > int(abs(unphase) - 10)) & (
                        abs(float(A.split(",")[2])) < int(abs(unphase) + 10))
            mag_flag = (float(A.split(",")[1]) > float(abs(ampt) - 0.1)) & (float(A.split(",")[1]) < float(ampt + 0.1))
            if ampt==0:
                phase_flag=True
            if mag_flag&phase_flag:
                break
            else:
                UART1.sendcmd("tune {}".format(ampt) + " {}\n".format(unphase))
                time.sleep(2)
                A = self.query_gamma(UART1)
                print(A)
                count=count+1
            if count==5:
                print("the set gamma is wrong")
                break
        return
    def read_S(self,UART1):
        return UART1.sendcmd("spar?\n")

    def query_gamma(self,UART1):
        return UART1.sendcmd("gamma?\n")

    def query_postion(self,UART1):
        return UART1.sendcmd("pos?\n")

    def init_tune(self,UART1):
        UART1.sendcmd("init\n")
        return True
    #def id_

    def get_freq_by_ch(self,ch):
        # defalut unit : MHz
        if int(ch) < 15:
            freq = (2407 + 5 * int(ch))
        elif (int(ch) > 30) and (int(ch) < 170):
            freq = (5000 + 5 * int(ch))
        else:
            freq = int(ch)
        # self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
        return freq

    def sweep_test(self):
        am_list = []
        ph_list = []

        intv = 15
        for am in range(9, -1, -1):
            # s=45
            # a=int(float(s/am))
            ampt = round((am / 10), 1)
            if ampt == 0.0:
                intv = 360
            elif (ampt > 0) & (ampt <= 0.2):
                intv = 40
            elif (ampt >= 0.3) & (ampt < 0.5):
                intv = 30
            elif (ampt >= 0.5) & (ampt <= 0.7):
                intv = 20
            else:
                intv = 15
            # print(ampt)
            for unphase in range(-180, 178, intv):
                start_time = time.time()
                # print(unphase)
                if ampt == 0.0:
                    unphase = 0

                # tuner1.set_tune(UART1, ampt, unphase)
                # time.sleep(0.2)
                am_list.append(ampt)
                ph_list.append(unphase)

        df = pd.DataFrame({'A': am_list, 'B': ph_list})
        df.to_csv('output_pd.csv', index=False)

        with open('output.csv', 'a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # 使用zip将两个列表按列组合
            for amp, phase in zip(am_list, ph_list):
                writer.writerow([amp, phase])


if __name__ == "__main__":
    tuner1=tuner()
    UART1 = Uart(17, wr_mode=True)
    UART1.set_baudrate("9600")
    UART1.open()
    tuner1.open(UART1)
    tuner1.init_tune(UART1)
    time.sleep(2)
    tuner1.load_file(UART1,"5500")
    time.sleep(2)

    for ch in [1,7,13,36,60,100,130,149,165]:
        freq = tuner1.get_freq_by_ch(ch)

        tuner1.load_file(UART1, str(freq))
        time.sleep(2)
        tuner1.set_tune(UART1, 0.2, 180)
        time.sleep(2)
        tuner1.set_tune(UART1, 0.1, -30)








    #tuner1.init_tune(UART1)
    tuner1.set_tune(UART1,0.2,180)
    #time.sleep(2)
    #tuner1.query_gamma(UART1)
    #time.sleep(1)
    #tuner1.read_S(UART1)
    #aaa=UART1.sendcmd("*IDN?\n")
    #print(aaa)
    #fprintf(host, '*idn?\n')
    #tuner1 = tuner()
    #aaa = tuner1.open()
    #tuner1.fprintf(tuner1,"*idn?\n")
    #print(tuner1.write('*idn?'))
    #aaa = tuner1.query("*idn?\n")



    #ZND1.set_mark(1,5800)
    #ZND1.set_freq(2000,5900)
    #time.sleep(0.5)
    #ZND1.set_Sparams("S11")


   #print(ZND1.read_mark_polar_real())
    #print(ZND1.read_mark_polar_imag())
    #print(ZND1.read_mark_smith_real())
    #print(ZND1.read_mark_smith_imag())
    #print(ZND1.read_mark_dbmsg())
    #print(ZND1.read_mark_real())
    #print(ZND1.read_mark_imag())
    UART1.close()