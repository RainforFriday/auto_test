from pyintf.uart import *
# from pyintf.agilent import *
from aicintf.agilent import *

from pyinstr.rs.Tuner import *
from pyinstr.rs.cmw import *
from pyinstr.rs.fsq import *
import pyvisa as visa
from pyintf.gpib import *
import time
import csv
import datetime


def tuner_init(tuner1,UART1,freq):
    tuner1.open(UART1)
    tuner1.init_tune(UART1)
    time.sleep(2)
    tuner1.load_file(UART1, str(freq))
    time.sleep(2)

def load_bin(UART2,bin_file_path):
    UART2.xmodem_load_bin("x 160000", bin_file_path)
    xxx = UART2.sendcmd("g 160000")
    print(xxx)

def fsq_init(fsqx):
    fsqx.set_analyzer_mode()
    # fsqx.set_span(100)

    fsqx.set_rb(1)
    fsqx.set_vb(3)
    fsqx.set_reflvl(30)
    # fsqx.set_cfreq(freq)
    time.sleep(0.5)

def meas_fsq(fsqx):
    fsqx.get_peak_mark()
    time.sleep(0.5)
    mark = fsqx.get_peak_mark()
    mark_pwr =str(round(float(mark[1]),2))
    freq = str(round(float(mark[0])/1000000,2))
    print(mark_pwr)
    print(freq)
    return mark_pwr,freq

def set_auto_ref_pwr(fsqx):
    # self.set_reflvl(30)
    time.sleep(1)
    pwr = fsqx.get_peak_mark()[1]
    if int(float(pwr))<30:
        fsqx.set_reflvl(int(float(pwr)) + 15)
        time.sleep(1)

def set_band(fsqx,start,stop,loss):
    fsqx.set_reflvl(30)
    fsqx.set_startfreq(start)
    fsqx.set_stopfreq(stop)
    set_auto_ref_pwr(fsqx)
    pwr, freq = meas_fsq(fsqx)
    pwr = round(float(pwr)+loss, 2)
    return str(pwr),freq

def mea_muti_freq(fsqx,loss):
    # fsq_init(fsqx, 200, 2400)
    pwr02,freq02=set_band(fsqx,30,5450,loss)
    pwr24,freq24=set_band(fsqx,5450,5550,loss)
    pwr25,freq25=set_band(fsqx,5550,10950,loss)
    pwr48,freq48=set_band(fsqx,10950,11050,loss)
    pwr50,freq50=set_band(fsqx,11050,16450,loss)
    pwr72,freq72=set_band(fsqx,16450,16550,loss)
    pwr75,freq75=set_band(fsqx,16550,26000,loss)


    return pwr02,freq02,pwr24,freq24,pwr25,freq25,pwr48,freq48,\
           pwr50,freq50,pwr72,freq72,pwr75,freq75

if __name__ == "__main__":

    freq = 5500

    UART2 = Uart(8, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # UART2.sendcmd("tone_off")

    tuner1 = tuner()
    UART1 = Uart(17, wr_mode=True)
    UART1.set_baudrate("9600")
    UART1.open()
    tuner_init(tuner1, UART1, freq)

    Agilent = agilent(5)
    Agilent.open()
    # Agilent.Cur_Mode()
    # time.sleep(0.5)
    # Agilent.OUTP_OFF()
    # Agilent.Cur_Mode()
    # Agilent.set_Chl1(3.3, 3)
    # Agilent.curtrange()
    # Agilent.OUTP_ON()
    # time.sleep(0.1)

    FSQ_IP = "10.21.10.179"
    fsqx = FSQ()
    fsqx.open_tcp(FSQ_IP, 5025)
    print(fsqx.id_string())
    fsq_init(fsqx)

    # # Once
    # bin_file_path = "./testmode22_2025_0703_1813.bin"
    # load_bin(UART2,bin_file_path)
    # time.sleep(5)

    # UART2.sendcmd("setch 100")
    # time.sleep(1)

    #     # reg_init1(UART2)
    #     # UART2.sendcmd("setch 100")

    # UART2.sendcmd("setrate 5 11")
    # UART2.sendcmd("setbw 1 1")
    # UART2.sendcmd("settx 1")
    # UART2.sendcmd("pwrmm 1")
    # UART2.sendcmd("setpwr 25")
    # UART2.sendcmd("settx 0")
    # time.sleep(0.2)



    # A = Agilent.meas_vot1()
    # B = Agilent.meas_curr1()
    #
    # # Agilent.close()

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    file=r'\\10.21.10.13\share\Data\aic8819\aic8819_Tuner_currentTest_5g_'+ current_time + ".csv"
    header = ['current_time', 'Freq', 'Amp', 'Phase', 'Current(mA)', 'Band1(0.03-5.45)', '', 'Band2(5.45-5.55)', '', 'Band(5.55-10.95)', '',
              'Band3(10.95-11.05)', '', 'Band(11.05-16.45)', '', 'Band(16.45-16.55)', '', 'Band(16.55-26)']
    if not os.path.exists(file):
        # os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

    intv=10

    for am in range(9, -1, -1):
        # s=45
        # a=int(float(s/am))
        ampt=round((am/10),1)
        if ampt == 0.0:
            intv=360
        # print(ampt)
        for unphase in range(-180,178, intv):
            start_time = time.time()
            # print(unphase)
            if ampt == 0.0:
                unphase=0

            tuner1.set_tune(UART1, ampt, unphase)

            # tuner1.set_tune(UART1, 0, unphase)
            b=tuner1.query_gamma(UART1)
            c=tuner1.query_postion(UART1)
            # print(c)
            print(b)
            values = b.strip().split(',')
            setAmp = float(values[1])  # 第二个值 (0.000)
            setPh = float(values[2])

            # UART2.sendcmd("tone_on 01 1 1ff f")
            time.sleep(0.5)
            UART2.sendcmd("w 4034409c	0000000c")

            time.sleep(0.5)
            loss = 1.2
            pwr02, freq02, pwr24, freq24, pwr25, freq25, pwr48, freq48, pwr50, freq50, \
            pwr72, freq72, pwr75, freq75 = mea_muti_freq(fsqx,loss)


            current_readings = []
            for _ in range(3):
                currs = float(Agilent.meas_curr1().strip()) * 1000
                time.sleep(0.2)
                current_readings.append(currs)
                print(f"第{_+1}次测量值：{currs:.2f} mA")

            curr = round(sum(current_readings) / len(current_readings), 2)

            UART2.sendcmd("w 4034409c	00000008")
            # UART2.sendcmd("tone_off")
            time.sleep(10)

            # print(curr)

            # time.sleep(5)
            # if ampt<0.3:
            #     time.sleep(2)
            # if ampt<0.6:
            #     time.sleep(3)
            # if ampt < 0.8:
            #     time.sleep(5)
            #UART1.reg_write("40344030", "1BCED868")

            DATA_LIST=[current_time+","+str(freq)+","+str(ampt)+","+str(unphase)+","+str(curr)+","+
                       pwr02+","+freq02+","+pwr24+","+freq24+","+pwr25+","+freq25+","+
                       pwr48+","+freq48+","+pwr50+","+freq50+","+pwr72+","+freq72+","+pwr75+","+freq75]

            with open(file, "a+") as  CSVFILE:
                CSVFILE.write(",".join(DATA_LIST) + "\n")

            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time  # 计算耗时

            print(f"code spand : {elapsed_time:.4f} s")  # 保留4位小数

    # finish
    UART2.close()
    fsqx.close()
    UART1.close()
    Agilent.OUTP_OFF()
    Agilent.close()
