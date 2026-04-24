import pyvisa as visa
from pyintf.gpib import *
import time


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


if __name__ == "__main__":
    Agilent=agilent(6)
    Agilent.open()
    #Agilent.Cur_Mode()
    #time.sleep(0.5)
    Agilent.OUTP_OFF()
    Agilent.Cur_Mode()
    Agilent.set_Chl1(3.3,3)
    Agilent.curtrange()
    Agilent.OUTP_ON()
    time.sleep(0.1)
    A=Agilent.meas_vot1()
    B=Agilent.meas_curr1()

    print(A)
    print(B)
    #Agilent.close()