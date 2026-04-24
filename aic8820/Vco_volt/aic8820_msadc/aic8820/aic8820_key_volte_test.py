import serial   # pip install pyserial
import serial.tools.list_ports
import re
import sys
import time
import pyprind
import xmodem
from aicintf.uart import *
from aicintf.com import *
from aicbasic.aiclog import *
from msadc import *
sys.path.append("..")

def load_bin():
    bin_file_path = "BIN/testmode_8820_0311_hlmc.bin"
    uart0.xmodem_load_bin("x 160000",bin_file_path)
    xxx = uart0.sendcmd("g 160000")
    print(xxx)
    time.sleep(3)
def load_BT_bin():
    bin_file_path = "BIN/fw_8820_btonly_4f3f_breqedr.bin"
    uart0.xmodem_load_bin("x 100000",bin_file_path)
    xxx = uart0.sendcmd("g 100000")
    print(xxx)
    time.sleep(3)
def read_csv():
    with open(csv_name,encoding='gb18030', errors='ignore') as CSV:
        txt=CSV.read().split("\n")
    NAME=[]
    MODE=[]
    ADDR=[]
    BIT=[]
    for i in range(1,len(txt),1):
        if txt[i]!="":
            item=txt[i].split(",")
            if item[0]!="":
                name = item[1] + "_" + item[2] + "_" + item[0]
                mode=item[len(item)-1]
                NAME.append(name)
                MODE.append(mode)
                for n in range(0,3,1):
                    ADDR.append(item[3+2*n].split("<")[0])
                   # print(BIT)
                    BIT.append(int(item[(4+2*n)].split("b")[1],2))

    #print(NAME)
    #print(MODE)
    #print(ADDR)
    #print(BIT)
    return NAME,MODE,ADDR,BIT
def read_ADDR():
    NAME,MODE,ADDR,BIT=read_csv()
    with open(csv_name1,encoding='gb18030', errors='ignore') as CSV:
        txt=CSV.read().split("\n")
    addr_name=[]
    addr=[]
    bit=[]
    for i in range(1, len(txt), 1):
        item = txt[i].split(",")
        #print(item[3])
        addr_name.append(item[3])
        addr.append(item[0])
        bit.append(item[2])
    #print(addr_name)
    #print(addr)
    #print(bit)
    N_addr=[]
    addr_real=[]
    bit_addr=[]
    for n in range(0, len(ADDR), 1):
        flag = 1
        while flag==1:
            for i in range(0,len(addr_name),1):
                if ADDR[n] not in addr_name:
                    if  ADDR[n] not in N_addr:
                        N_addr.append(ADDR[n])
                        print(ADDR[n]+" not found addr")
                    flag=0
                else:
                    if ADDR[n]==addr_name[i]:
                        addr_real.append(addr[i])
                        bit_addr.append(bit[i])
                        flag=0
    if N_addr!=[]:
        print(N_addr)
        exit()
    #print(addr_real)
    #print(bit_addr)
    #print(BIT)
    return addr_real,bit_addr,BIT,NAME,MODE
def wifi_mode():
    uart0.sendcmd("settx 0")
    uart0.sendcmd("setrate 2 7")
    uart0.sendcmd("pwrmm 1")
    uart0.sendcmd("setpwr 16")
    uart0.sendcmd("settx 1")
    uart0.sendcmd("settx 0")
def BT_mode():
    uart0.sendcmd("set_mode 0")
    uart0.sendcmd("set_pkt 0x11")
    uart0.sendcmd("set_pattern 0x00")
    uart0.sendcmd("set_addr 0A 1C 6B C6 96 7E")
    uart0.sendcmd("settx 1")
    uart0.sendcmd("settx 0")
def WF_TX_hb_ON():
    uart0.sendcmd("setch 100")
    time.sleep(1)
    uart0.write_reg_mask("40344088", "22:21", 3)
def WF_TX_hb_OFF():
    uart0.write_reg_mask("40344088", "21", 0)
def WF_TX_ON():
    #uart0.sendcmd("setch 7")
    time.sleep(1)
    uart0.write_reg_mask("40344088", "22:21", 3)
def WF_TX_OFF():
    uart0.write_reg_mask("40344088", "21", 0)
def WF_PLL_ON():
    pass
def WF_PLL_OFF():
    pass
def BT_TX_ON():
    uart0.write_reg_mask("40622040", "15:14", 3)
def BT_TX_OFF():
    uart0.write_reg_mask("40622040", "14", 0)
def USB_ON():
    uart0.write_reg_mask("4024100c", "17:14",15)
    uart0.write_reg_mask("4024100c", "25:24", 3)
def USB_OFF():
    uart0.write_reg_mask("4024100c", "31:0", 0)
def PCIE_ON():
    uart0.write_reg_mask("40780014", "5:4", 3)
    uart0.write_reg_mask("40780014", "15:14", 3)
    uart0.write_reg_mask("40780000", "15", 1)
def PCIE_OFF():
    uart0.write_reg_mask("40780014", "5", 0)
    uart0.write_reg_mask("40780014", "15", 0)

def WF_RX_ON():
    uart0.sendcmd("setch 100")
    time.sleep(1)
    uart0.write_reg_mask("40344088", "20:19", 3)

def WF_RX_OFF():
    uart0.write_reg_mask("40344088", "19", 0)

def WF_RX_hb_ON():
    uart0.sendcmd("setch 100")
    time.sleep(0.5)
    uart0.write_reg_mask("40344088", "20:19", 3)

def WF_RX_hb_OFF():
    uart0.write_reg_mask("40344088", "19", 0)

def BT_RX_ON():
    uart0.write_reg_mask("40622040", "13:12", 3)
def BT_RX_OFF():
    uart0.write_reg_mask("40622040", "12", 0)

def config_on(i):
    uart0.write_reg_mask(str(addr_real[3 * i]), bit_addr[3 * i], BIT[3 * i])
    uart0.write_reg_mask(str(addr_real[3 * i + 1]), bit_addr[3 * i + 1], BIT[3 * i + 1])
    uart0.write_reg_mask(str(addr_real[3 * i + 2]), bit_addr[3 * i + 2], BIT[3 * i + 2])
    time.sleep(0.01)
    if int(BIT[3 * i])== 12:
        DVDD=str(adc.ms_portdc_usb_on())
    else:
        DVDD=str(adc.ms_portdc())
    return str(DVDD)

def config_off(i):
    #eval(MODE[i].split("ON")[0] + "OFF" + "()")
    uart0.write_reg_mask(str(addr_real[3 * i]), bit_addr[3 * i], 0)
    uart0.write_reg_mask(str(addr_real[3 * i + 1]), bit_addr[3 * i + 1], 0)
    uart0.write_reg_mask(str(addr_real[3 * i + 2]), bit_addr[3 * i + 2], 0)
    time.sleep(0.01)
def mea_volt():
    for i in range(0,int(len(addr_real)/3),1):
        if MODE[i] == "BT_TX_ON" or MODE[i] == "BT_RX_ON":
            dvdd="null"
        else:
            #eval(MODE[i] + "()")
            dvdd = config_on(i)
            config_off(i)
        with open("./" + dvdd_wifi_result, "a+", ) as  CSVFILE:
            CSVFILE.write(BOR+ "," +str(NAME[i])+","+str(dvdd)+","+str(MODE[i])+"\n")

def mea_bt_volt():
    for i in range(0,int(len(addr_real)/3),1):
        if MODE[i]=="BT_TX_ON" or MODE[i]=="BT_RX_ON":
            #eval(MODE[i] + "()")
            dvdd=config_on(i)
            config_off(i)
        else:
            dvdd = "null"
        with open("./" + dvdd_bt_result, "a+", ) as  CSVFILE:
            CSVFILE.write(BOR+ "," +str(NAME[i])+","+str(dvdd)+","+str(MODE[i])+"\n")

def mea_volt3():
    for i in range(0,int(len(addr_real)/3),1):
        if MODE[i] == "BT_TX_ON" or MODE[i] == "BT_RX_ON":
            dvdd="null"
        else:
            #eval(MODE[i] + "()")
            # dvdd = config_on(i)

            dvdd_measurements = []
            for _ in range(3):  # 测量3次
                dvdd = config_on(i)
                dvdd_measurements.append(str(dvdd))  # 将每次测量结果转为字符串存储

            # 将3次测量结果用逗号连接
            dvdd_str = ",".join(dvdd_measurements)


            config_off(i)
        with open("./" + dvdd_wifi_result, "a+", ) as  CSVFILE:
            CSVFILE.write(BOR+ "," +str(NAME[i])+","+dvdd_str+","+str(MODE[i])+"\n")

if __name__ == "__main__":
    global uart0,csv_name,cva_name1,dvdd_result0
    csv_name = "aic8820h_spec_testability(2).csv"
    csv_name1="aic8820h_addr_sheet.csv"
    dvdd_wifi_result="./result/aic8820D80_0811_test2.csv"
    dvdd_bt_result="aic8820h1_bt_70.csv"
    addr_real,bit_addr,BIT,NAME,MODE= read_ADDR()
    BOR="buf_8"
    comport = 8
    uart0 = uart_open(comport)
    #mea_item="wifi"
    mea_item="wifi"
    uart0.sendcmd("tc 0")
    if mea_item=="wifi":
        #load_bin()
        adc = MSADC()
        #wifi_mode()
        # mea_volt()
        mea_volt3()
    if mea_item=="bt":
        load_BT_bin()
        adc = MSADC()
        BT_mode()
        mea_bt_volt()
    uart_close()