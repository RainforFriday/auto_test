import pyvisa as visa

class gpib:
    def __init__(self,comport=5):
        self.ser=visa.ResourceManager()
        self.addr=self.ser.open_resource("GPIB0::{}::INSTR".format(self.comport))
        A=self.addr.query('*IDN?')
        self.addr.write("*CLS")
        self.addr.write("STAT:PRES")
        self.addr.write("*SRE 0")
        self.addr.write("*ESE 0")
        return A

    def set_Chl1(self,volt1,cur1):
        self.write("VOLT {}".format(self.volt1))
        self.write("CURR {}".format(self.cur1))

    def set_Chl2(self,volt2,cur2):
        self.write("VOLT2 {}".format(self.volt2))
        self.write("CURR2 {}".format(self.curr2))

    def OUTP_ON(self):
        self.write("OUTP ON")

    def OUTP_OFF(self):
        self.write("OUTP OFF")

    def currange(self,Currange=0.02):
        if Currange in["0.02","1","3","MAX","MIN"]:
            self.write("SENS:CURR:RANG {}".format(self.currange))
        else:
            print("set currange{}is error".format(self.Currange))
        return False
    def meas_curr1(self):
        return self.query("MEAS:CURR?")

    def meas_curr2(self):
        return self.query("MEAS:CURR2?")

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
        # self.ser.reset_output_buffer()
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
            self.ser.set_buffer_size(rx_size=25600, tx_size=10000)
            if "\r" not in cmdstr:
                cmdstr = cmdstr + "\r"
            cmd_byte = cmdstr.encode()
            # self.ser.reset_output_buffer()
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


    def read_adc_dump_data(self, cmdstr=''):
        # self.ser.reset_output_buffer()
        if self.ser.isOpen() is False:
            wlogerror('Com is not open!')
            return ''

        # input command string check
        # matchstr = re.findall(r'^[\w+\s+]+$',cmdstr,re.M);
        # if matchstr==[]:
        #    logwarn('Cmd syntax is error!');
        #    return '';
        try:
            self.ser.timeout = 1
            self.ser.flushInput()
            self.ser.flushOutput()
            #self.ser.set_buffer_size(rx_size=25600, tx_size=25600)

            if "\r" not in cmdstr:
                cmdstr = cmdstr + "\r"
            cmd_byte = cmdstr.encode()
            # self.ser.reset_output_buffer()
            # self.ser.write((cmdstr+'\r').encode())
            self.ser.write(cmd_byte)
            wlog("COM CMD: "+cmdstr)
            time.sleep(0.2)
            ser_result =self.ser.readall()
            time.sleep(0.2)
            ser_result = str(ser_result, encoding="utf-8").strip()
            # print(ser_result)
            wlogdebug(ser_result)
            return ser_result.split("\n")
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

    def xmodem_getc(self, size, timeout=1):
        return self.ser.read(size)

    def xmodem_putc(self, data, timeout=1):
        return self.ser.write(data)

    def xmodem_putc_user(self, data, timeout=1):
        return self.ser.write(data)

    def xmodem_load_bin(self, CMD="x 160000", BIN_PATH=""):
        """
        :param CMD:
        :param BIN_PATH:
        :return:
        com = COM(3)
        com.open()
        bin_file_path = "./testmode_lite_u02.bin"
        com.xmodem_load_bin("x 160000", bin_file_path)
        xxx = com.sendcmd("g 160000")
        com.close()
        """
        self.ser.flushInput()
        self.ser.flushOutput()
        if not CMD.endswith("\r"):
            cmd = CMD + "\r"
        else:
            cmd = CMD
        self.ser.write(cmd.encode())
        # time.sleep(0.2)
        NUM = 0
        while True:
            cvalue = self.ser.read(1)
            value = str(cvalue, encoding="utf-8")
            #print(value.strip())
            if value == 'C':
                NUM = NUM + 1
                if NUM == 4:
                    print("Start To Load Bin File....")
                    break
        time.sleep(0.1)
        bin_path = BIN_PATH
        # download firmware in 2M mode
        stream = open(bin_path, 'rb')
        m = xmodem.XMODEM(self.xmodem_getc, self.xmodem_putc_user, mode="xmodem1k")
        m.send(stream)
        print("Load Bin Suceess")


if __name__ == "__main__":
    com = COM(8)
    com.open()
    bin_file_path = "./lmacfw_jifeng.bin"
    com.xmodem_load_bin("x 160000", bin_file_path)
    xxx = com.sendcmd("g 160000")
    print(xxx)
    com.close()

gpib_addr = 'GPIB0::5::INSTR'
# Create an object of visa_dll
rm = visa.ResourceManager()
# Create an instance of certain interface(GPIB and TCPIP)
#tcp_inst = rm.open_resource(tcp_addr)
gpib_inst = rm.open_resource(gpib_addr)
# Command '*IDN?' can fetch instrument info
# Using write()/read()/query() function to make communication with device
# according to the command type
#print(tcp_inst.query('*IDN?'))
print(gpib_inst.query('*IDN?'))
#gpib_inst.write("OUTP OFF")
gpib_inst.write("OUTP ON")
gpib_inst.close()