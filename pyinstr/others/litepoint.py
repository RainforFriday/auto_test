import hostport as hostport

from pyinstr.rs.genericinstrument import *
from pyintf.uart import *
from pybasic.hplog import *

__version__ = "v0.1"


class LitePoint(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()


def LP_init(LP1):
    LP1.write("DCL:HMOD")
    LP1.write("CLS")
    LP1.write("RST")
    LP1.write("SYS;FORM:READ:DATA ASC")
    LP1.write("ROUT1;PORT:RES:ADD RF1A,VSA1")
    LP1.write("ROUT1;PORT:RES:SUBT RF1A,VSG1")
    LP1.write("CHAN1;WIFI")
    #LP1.write("VSA1;RLEV 30")
    LP1.write("VSA1;RLEV:AUTO:TIME 0.000001")
    LP1.write("VSA1;SRAT 240000000")
    LP1.write("VSA1;CAPT:TIME 0.01")
    LP1.write("VSA1;INIT")


def CSV_MCS11(csv_name, INDEX, DATA_LIST):
    with open(csv_name, "a+") as  CSVFILE:
        CSVFILE.write(INDEX + "," + ",".join(DATA_LIST) + "\n")
    #print(power_result_ch)
    #print(evm_result_ch)


def ccc(args):
    pass


def MCS11_Send(uartx):
    uartx.sendcmd("settx 0")
    uartx.sendcmd("setch 36")
    uartx.sendcmd("setbw 1 1")
    uartx.sendcmd("setrate 5 11")
    #UART1.sendcmd("setlen 2000")
    uartx.sendcmd("settx 100000")

def MCS9_Send(uartx):
    uartx.sendcmd("settx 0")
    uartx.sendcmd("setch 36")
    uartx.sendcmd("setbw 1 1")
    uartx.sendcmd("setrate 4 9")
    #UART1.sendcmd("setlen 2000")
    uartx.sendcmd("settx 100000")

def MCS7_Send(uartx):
    uartx.sendcmd("settx 0")
    uartx.sendcmd("setch 36")
    uartx.sendcmd("setbw 1 1")
    uartx.sendcmd("setrate 2 7")
    #UART1.sendcmd("setlen 2000")
    uartx.sendcmd("settx 100000")

def reg_init(uartx):
    uartx.reg_write("40344038", "19d78bc8")
    uartx.reg_write("4034403c", "058048f6")
    uartx.reg_write("40580108", "00001f04")
    uartx.reg_write("50018808", "83084241")
    uartx.reg_write("50019124", "101BF1C0")

def test_u02(uartx,LP1, LOSS=0.6):
    EVM_R = []
    PWR_R = []
    power_x = []
    evm_x = []
    for ch in range(36, 168,10):
        uartx.sendcmd("setch " + str(ch))
        #if ch < 100:
            #uartx.reg_write("40344030", "7A2A5008")
        #elif ch < 140:
            #uartx.reg_write("40344030", "791B50C8")
        #else:
            #pass
            #uartx.reg_write("40344030", "7A2AD0C8")
            #uartx.reg_write("40344030", "791B50C8")
        # #else:
            #UART1.reg_write("40344030", "7A2AD0E8")
        # print(str(ch) + ":" + UART1.reg_read("40344030"))
        freq = 5180000000 + (ch - 36) * 5000000
        LP1.write("VSA1;FREQ:cent " + str(freq))

        for i in range(8):
            LP_init(LP1)
            LP1.write("WIFI;CLEAR:ALL")
            time.sleep(0.1)
            LP1.write("WIFI;CALC:TXQ 0,1")
            EVM = LP1.query("FETC:SEGM1:OFDM:EVM:DATA:AVER?")
            LP1.write("WIFI;CLE:ALL")
            LP1.write("WIFI;CALC:POW 0,1")
            POWER = LP1.query("WIFI;FETC:POW:AVER?")
            if POWER[0] == "0" and EVM.split(",")[0] == "0":
                a = (float(POWER[2:])+LOSS)
                b = (float(EVM[2:]))
                power_x.append(a)
                evm_x.append(b)
            else:
                print("ERROR!" + POWER + " " + EVM)
            time.sleep(0.1)
        power_result = sum(power_x) / len(power_x)
        evm_result = sum(evm_x) / len(evm_x)
        evm_max = max(evm_x)
        EVM_R.append(str(round(evm_result, 2)))
        PWR_R.append(str(round(power_result, 2)))

        # LP1.write("VSA1;RLEV peak_pwr")
        time.sleep(0.02)
    print(EVM_R)
    print(PWR_R)
    #csv_init(EVM_R, PWR_R)
    return EVM_R, PWR_R

if __name__ == "__main__":
    host = "10.21.10.196"
    port = 24000

    csv_name = "AIC8800_U02_MCS11_1223_A21.csv"

    LP1 = LitePoint()
    LP1.open_tcp(host,port)
    uartx = Uart(7, wr_mode=True)
    uartx.set_baudrate(921600)
    uartx.open()
    ana_index = ["f", "e", "d", "c", "b", "a", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
    dig_index_mcs7 = "b"
    dig_index_mcs9 = "0"
    dig_index_mcs11 = "0"

    pwr_index_mcs7 = []
    pwr_index_mcs9 = []
    pwr_index_mcs11 = []

    for aindex in ana_index:
        pwr_index_mcs7.append(aindex + dig_index_mcs7)
        pwr_index_mcs9.append(aindex + dig_index_mcs9)
        pwr_index_mcs11.append(aindex + dig_index_mcs11)

    SA = True

    BOR_NO = "A21_1.7n_1.3p_0.6P"

    if SA == True:

        MCS7_Send(uartx)
        reg_init(uartx)
        LP1.write("VSA1;RLEV 30")
        # for pwr_index in pwr_index_mcs11:
        for pwr_index in ["f6"]:  # ["30","20","10","00"]:
            uartx.sendcmd("setpwr " + pwr_index)
            EVM_R_MCS7, PWR_R_MCS7 = test_u02(uartx, LP1)
            peak_pwr = int(float(PWR_R_MCS7[0])) + 15
            if peak_pwr > 30:
                peak_pwr = 30
            LP1.write("VSA1;RLEV " + str(peak_pwr))
            print("PEAK_PWR: " + str(peak_pwr))
            # print(PWR_R_MCS9)
            # print(EVM_R_MCS9)
            CSV_MCS11(csv_name, BOR_NO + "_MCS7_PWR_" + pwr_index, PWR_R_MCS7)
            CSV_MCS11(csv_name, BOR_NO + "_MCS7_EVM_" + pwr_index, EVM_R_MCS7)

    if SA == False:

        MCS9_Send(uartx)
        reg_init(uartx)
        LP1.write("VSA1;RLEV 30")
        # for pwr_index in pwr_index_mcs11:
        for pwr_index in ["fb"]:  # ["30","20","10","00"]:
            uartx.sendcmd("setpwr " + pwr_index)
            EVM_R_MCS9, PWR_R_MCS9 = test_u02(uartx, LP1)
            peak_pwr = int(float(PWR_R_MCS9[0])) + 15
            if peak_pwr > 30:
                peak_pwr = 30
            LP1.write("VSA1;RLEV " + str(peak_pwr))
            print("PEAK_PWR: " + str(peak_pwr))
            # print(PWR_R_MCS9)
            # print(EVM_R_MCS9)
            CSV_MCS11(csv_name, BOR_NO + "_MCS9_PWR_" + pwr_index, PWR_R_MCS9)
            CSV_MCS11(csv_name, BOR_NO + "_MCS9_EVM_" + pwr_index, EVM_R_MCS9)

    if SA == True:

        MCS11_Send(uartx)
        reg_init(uartx)
        LP1.write("VSA1;RLEV 30")
        #for pwr_index in pwr_index_mcs11:
        for pwr_index in ["f0"]:#["30","20","10","00"]:
            uartx.sendcmd("setpwr "+pwr_index)
            EVM_R_MCS11,PWR_R_MCS11 = test_u02(uartx,LP1)
            peak_pwr = int(float(PWR_R_MCS11[0])) + 15
            if peak_pwr > 30:
                peak_pwr = 30
            LP1.write("VSA1;RLEV " + str(peak_pwr))
            print("PEAK_PWR: " + str(peak_pwr))
            #print(PWR_R_MCS9)
            #print(EVM_R_MCS9)
            CSV_MCS11(csv_name, BOR_NO+"_MCS11_PWR_"+pwr_index,PWR_R_MCS11)
            CSV_MCS11(csv_name, BOR_NO+"_MCS11_EVM_"+pwr_index,EVM_R_MCS11)

        LP1.close()
        uartx.close()


    #try:
        #power_result_ch=[]
        #evm_result_ch=[]
        #uartx.reg_write("50019124", "101BF0C0")
        #uartx.reg_write("50019124", "101BF1C0")
        #for ch in range(36,169,5):
          # power_x = []
           # evm_x = []
           # uartx.sendcmd("setch "+str(ch))

        ''' if (ch > 97) and (ch < 137):
            uartx.reg_write("40344030", "781BD0E8")
        elif (ch > 66) and (ch <= 97):
            uartx.reg_write("40344030", "7A2AD0C8")
        elif ch >= 137:
            uartx.reg_write("40344030", "7B1BD0E8")
        else:
            uartx.reg_write("40344030", "7A2A5008")
       
        
       if ch > 70:
            uartx.reg_write("40344030", "7A2AD0C8")
        else:
            uartx.reg_write("40344030", "7A2ED008")
       
        # uartx.reg_write("40344030","7A2A5008")
        # print("40344030 value:"+aaa)
        # uartx.sendcmd("setrate 2 7 ")
        #if ch > 100:
           # uartx.reg_write("40344030","7A2A48E8")
        #else:
            #uartx.reg_write("40344030","7A2A5008")
            #print("40344030 value:"+aaa)
        #uartx.sendcmd("setrate 2 7 ")

        f = 5180000000+(ch-36)*5000000
        LP1.write("VSA1;FREQ:cent "+str(f))
        for i in range(8):
            LP_init(LP1)
            LP1.write("WIFI;CLEAR:ALL")
            time.sleep(0.1)
            LP1.write("WIFI;CALC:TXQ 0,1")
            EVM = LP1.query("FETC:SEGM1:OFDM:EVM:DATA:AVER?")
            LP1.write("WIFI;CLE:ALL")
            LP1.write("WIFI;CALC:POW 0,1")
            POWER = LP1.query("WIFI;FETC:POW:AVER?")
            if POWER[0] == "0" and EVM.split(",")[0]== "0":
                a = (float(POWER[2:]))
                b = (float(EVM[2:]))
                power_x.append(a)
                evm_x.append(b)
            else:
                print("ERROR!"+POWER+" "+EVM)
            time.sleep(0.1)
        power_result = sum(power_x)/len(power_x)
        evm_result = sum(evm_x)/len(evm_x)
        #evm_max =max(evm_x)
        power_result_ch.append(str(round(power_result, 2)))
        evm_result_ch.append(str(round(evm_result,2)))
        time.sleep(0.2)
    csv_name = "AIC8800_U02_ch_5G_x3.csv"
    print(power_result_ch)
    print(evm_result_ch)
    with open(csv_name, "a") as  CSVFILE:
        CSVFILE.write("A21_MCS7,"+",".join(power_result_ch+evm_result_ch)+"\n")
    uartx.sendcmd("settx 0 ")
    LP1.close()
    uartx.close()
except:
    logexc()
    uartx.sendcmd("settx 0 ")
    LP1.close()  
    uartx.close()'''