from pyintf.uart import *
from pyinstr.rs.Tuner import *
from pyinstr.rs.cmw import *
from pyinstr.rs.fsq import *
import pyvisa as visa
from pyintf.gpib import *
import time
import csv

def tuner_init(tuner1,UART1,freq):
    tuner1.open(UART1)
    tuner1.init_tune(UART1)
    time.sleep(2)
    tuner1.load_file(UART1, str(freq))
    time.sleep(2)

class agilent(GPIB):
    def __init__(self, com_port=3):
        super(agilent, self).__init__(com_port)
        #self.query('*IDN?')
        self.ser = visa.ResourceManager()
        self.addr = "GPIB0::{}::INSTR".format(self.PortNum)
        self.resourceManager = visa.ResourceManager()
        self.instance =self.resourceManager.open_resource(self.addr)
    def open(self):
        self.idn = self.instance.query('*IDN?')
        self.instance.write("SENS:CURR:RANG llOCAL")
        time.sleep(0.2)
        #self.instance.write("*CLS")
        #self.instance.write("STAT:PRES")
        #self.instance.write("*SRE 0")
        #self.instance.write("*ESE 0")
        print(self.idn)
    def close(self):
        self.instance.write("*CLS")
        self.instance.write("STAT:PRES")
        self.instance.write("*SRE 0")
        self.instance.write("*ESE 0")
    def set_Chl1(self,volt1,cur1):
        self.instance.write("VOLT {}".format(volt1))
        self.instance.write("CURR {}".format(cur1))

    def set_Chl2(self,volt2,cur2):
        self.instance.write("VOLT2 {}".format(volt2))
        self.instance.write("CURR2 {}".format(cur2))

    def OUTP_ON(self):
        self.instance.write("OUTP ON")

    def OUTP_OFF(self):
        self.instance.write("OUTP OFF")

    def curtrange(self,Currange="3"):
        if Currange in["0.02","1","3", "MAX" ,"MIN"]:
            self.instance.write("SENS:CURR:RANG {}".format(Currange))
        else:
            print("set currange {} is error".format(Currange))
        return False

    def Cur_Mode(self,mode="LLOCAL"):
        if mode in["LLOCAL","LREMOTE","HLOCAL","HREMOTE"]:
            self.instance.write("OUTP:COMP:MODE {}".format(mode))
            time.sleep(0.2)
            #print(mode)
        else:
            print("set Cur_mode {} is error".format(mode))
        return False
    def meas_curr1(self):
        time.sleep(0.1)
        return self.instance.query("MEAS:CURR1?")

    def meas_curr2(self):
        time.sleep(0.1)
        return self.instance.query("MEAS:CURR2?")

    def meas_vot1(self):
        time.sleep(0.1)
        return self.instance.query("MEAS:VOLT1?")
    def meas_vot2(self):
        time.sleep(0.1)
        return self.instance.query("MEAS:VOLT2?")

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
    pwr02,freq02=set_band(fsqx,30,2400,loss)
    pwr24,freq24=set_band(fsqx,2400,2500,loss)
    pwr25,freq25=set_band(fsqx,2500,4800,loss)
    pwr48,freq48=set_band(fsqx,4800,5000,loss)
    pwr50,freq50=set_band(fsqx,5000,7200,loss)
    pwr72,freq72=set_band(fsqx,7200,7500,loss)
    pwr75,freq75=set_band(fsqx,7500,26000,loss)


    return pwr02,freq02,pwr24,freq24,pwr25,freq25,pwr48,freq48,\
           pwr50,freq50,pwr72,freq72,pwr75,freq75

if __name__ == "__main__":

    freq = 2442

    UART2 = Uart(4, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # UART2.sendcmd("tone_off")

    tuner1 = tuner()
    UART1 = Uart(12, wr_mode=True)
    UART1.set_baudrate("9600")
    UART1.open()
    tuner_init(tuner1, UART1, freq)

    Agilent = agilent(6)
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

    # UART2.sendcmd("setch 7")
    # time.sleep(1)

    #     # reg_init1(UART2)
    #     # UART2.sendcmd("setch 7")

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


    file=r'\\10.21.10.13\share\Data\aic8819\aic8819_Tuner_currentTest.csv'
    header = ['Freq', 'Amp', 'Phase', 'Current(mA)', 'Band1(0.2-2.4)', '', 'Band2(2.4-2.5)', '', 'Band3(2.5-4.8)', '',
              'Band(4.8-5)', '', 'Band(5-7.2)', '', 'Band(7.2-7.5)', '', 'Band(7.5-26)', '', ]
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

            DATA_LIST=[str(freq)+","+str(ampt)+","+str(unphase)+","+str(curr)+","+
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
    Agilent.close()
