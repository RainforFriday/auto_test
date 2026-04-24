import serial   # pip install pyserial
import serial.tools.list_ports
import re
import sys
sys.path.append("..")
import pyprind
from pybasic.hplog import *


class COM:
    def __init__(self, comport=1):
        self.PortNum = comport
        self.ser = None
        self.baudrate = 928571
        self.timeout = None

    def open(self):
        try:
            self.ser = serial.Serial("COM"+str(int(self.PortNum)))
        except Exception as e:
            wlogerror("ACESS COM{} is denied!!!".format(self.PortNum))
            return False

        # set com options
        self.ser.baudrate = self.baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = self.timeout
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.interCharTimeout = None

        if self.ser.isOpen() is True:
            wlog('Com{} is open'.format(self.PortNum))
            return True
        else:
            wlogerror('Can not open Com{}'.format(self.PortNum))
            return False

    def close(self):
        try:
            self.ser.close()
        except Exception as e:
            wlogwarn('The COM{} is not open'.format(self.PortNum))
            return False

        if self.ser.isOpen() is False:
            wlog('Com{} is closed'.format(self.PortNum))
            return True
        else:
            wlogerror('Fail to close Com{}'.format(self.PortNum))
            return False

    def is_open(self):
        return self.ser.isOpen()

    def sendcmd(self, cmdstr=''):
        if self.ser.isOpen() is False:
            wlogerror('Com is not open!')
            return ''

        # input command string check
        # matchstr = re.findall(r'^[\w+\s+]+$',cmdstr,re.M);
        # if matchstr==[]:
        #    logwarn('Cmd syntax is error!');
        #    return '';
        try:
            self.ser.timeout = self.timeout
            self.ser.flushInput()
            self.ser.flushOutput()

            if "\r" not in cmdstr:
                cmdstr = cmdstr + "\r"
            cmd_byte = cmdstr.encode()
            # self.ser.write((cmdstr+'\r').encode())
            self.ser.write(cmd_byte)
            wlog("COM CMD: "+cmdstr)
            time.sleep(0.2)
            ser_result = self.ser.read(self.ser.in_waiting)
            com_return_value = str(ser_result, encoding="utf-8")
            wlogdebug(com_return_value)
            return com_return_value
        except Exception as e:
            wlogerror(sys.exc_info())
            wlogerror('fail to send command to com')
            self.ser.timeout = None
            return ''

    @staticmethod
    def port_list():
        return serial.tools.list_ports.comports()

    def set_baudrate(self, baudrate=921600):
        self.baudrate = baudrate


if __name__ == "__main__":
    com = COM(3)
    com.open()
    try:
        for i in range(1000):
            xxx = com.sendcmd("mw 4034206c 10800001")
            print(xxx)
            yyy = com.sendcmd("md 4034206C")
            print(yyy)
            print(i)
            time.sleep(0.1)
    except Exception as e:
        wlogerror(e)
        com.close()
    com.close()
