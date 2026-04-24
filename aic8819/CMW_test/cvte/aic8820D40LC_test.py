from pyintf.uart import *
from pyinstr.rs.cmw import *
import datetime


def CSV_MCS(csv_name,DATA_LIST):
    with open("./"+csv_name, "a+",) as  CSVFILE:
        CSVFILE.write(",".join(DATA_LIST) + "\n")


def cmw_intial():

    CMW1.wlan_set_route()
    CMW1.wlan_set_freq(2412e+6)
    CMW1.wlan_set_peakpwr(30)
    # CMW1.wlan_set_standard("11ac")  ## MCS7: F7    MCS11: F0
    CMW1.wlan_set_bandwidth("BW20")


def test(UART1,offst,rate,rate_g,mode,pwrlvl,CH,loss):
    for i in range(0, 3, 1):
    # for i in range(1, 2, 1):
        UART1.sendcmd("setrate " + str(rate[i]) + " " + str(rate_g[i]))

        if rate_g[i] == 0:
            len = 1500
            a = "11b"
        elif rate_g[i] == 8:
            len = 1500
            a = "11ac"
        else:
            len = 1500
            a = "11g"
        CMW1.wlan_set_standard(a)
        UART1.sendcmd("setlen " + str(len))
        UART1.sendcmd("setintv " + str(1000))
        for ch1 in CH:
            DATE = []
            UART1.sendcmd("settx 0")
            UART1.sendcmd("setch " + str(ch1))
            time.sleep(1)
            UART1.sendcmd("settx 1")
            if ch1 < 30:
                freq = 2412000000 + (ch1 - 1) * 5000000
            else:
                freq = 5180000000 + (ch1 - 36) * 5000000
            CMW1.wlan_set_freq(freq)
            time.sleep(0.5)
            CMW1.wlan_meas_start(1)
            time.sleep(1)
            if rate_g[i]==0:
                evm = str(round(float(CMW1.wlan_meas_11b_evm()), 2))
                pwr = str(round(float(CMW1.wlan_meas_11b_pwr()) + loss, 2))
            else:
                evm = str(round(float(CMW1.wlan_meas_evm()), 2))
                pwr = str(round(float(CMW1.wlan_meas_pwr()) + loss, 2))

            cmdx = ""
            try:
                cmdx = cmdx + UART1.sendcmd('r 403422c8')
                # print(cmdx)
            except:
                cmdx = "ERROR"

            for key_str in [",", "\n", "\r", "aic>"]:
                cmdx = cmdx.replace(key_str, " ")

            print(f"ch:{ch1}    pwr:{pwr}")
            print(f"cmdx:  {cmdx}")
            offset = float(pwr) - pwrlvl[i]
            result = "pass"
            if offset > 4:
                result = "fail"
            DATE = [BOR_NO + "," + mode[i] + "," + "20M" + "," + str(pwrlvl[i]) + "," + str(len) + "," + str(offst)+"," +
                    str(ch1) + "," + pwr + "," + evm + "," + str(round(offset,2)) + "," + result + "," + cmdx]
            CSV_MCS(csv_name, DATE)


if __name__ == "__main__":
    UART1 = Uart(18, wr_mode=True)
    UART1.set_baudrate("921600")

    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    # csv_name = "./data2/aic8800_D40LC_test_"+current_time+".csv"
    csv_name = "./data2/aic8800_D40LC_test_1.csv"
    UART1.open()

    host = "10.21.10.124"
    port = 5025
    CMW1 = CMW()
    CMW1.open_tcp(host, port)
    print(CMW1.id_string())
    cmw_intial()

    SA = True

    offst=0

    rate_2g = [0, 4, 11]
    rate1 = [0, 0, 0]
    pwrlvl_2g = [15, 16, 16]
    ch_2g = [1, 7, 13]
    loss_2g = 0.6
    mode_2g = ["11b_1M", "11g_6M", "11g_54M"]

    rate_5g = [4, 11, 8]
    rate2 = [0, 0, 4]
    pwrlvl_5g = [15, 15, 15]
    ch_5g = [36, 64, 100, 120, 136, 165]
    loss_5g = 1
    mode_5g = ["11a_6M", "11a_54M", "VHT_MCS8"]
    BOR_NO = "NO1"

    if SA == True:
        for d in range(1,3,1):
        # for d in range(1,2,1):
            for e in range(0,3,1):
            # for e in range(1,2,1):
                if d==1:
                    UART1.sendcmd("pwrlvl " + str(d) + " " + str(rate1[e]) + " " + str(rate_2g[e]) + " " + str(pwrlvl_2g[e]))
                    time.sleep(0.5)
                else:
                    if (rate2[e]==4)|(rate2[e]==2):
                        mode=1
                    elif (rate2[e]==0):
                        mode=0
                    else:
                        mode=2
                    UART1.sendcmd(
                        "pwrlvl " + str(d) + " " + str(mode) + " " + str(rate_5g[e]) + " " + str(pwrlvl_5g[e]))
                    time.sleep(0.5)
        # for a in range(1,3,1):
        #     if a==1:
        #         num=3
        #     else:
        #         num=6
        #     for c in range(0,3,1):
        #         for b in range(0,num,1):
        #             UART1.sendcmd("pwrofst " + str(a)+" "+str(c)+" "+str(b)+" "+str(offst))
        #             time.sleep(0.5)

        UART1.sendcmd("settx 0")
        UART1.sendcmd("setbw 0 0")
        CMW1.wlan_set_bandwidth("BW20")
        CMW1.wlan_set_peakpwr(30)
        test(UART1,offst,rate1,rate_2g,mode_2g,pwrlvl_2g,ch_2g,loss_2g)
        test(UART1, offst,rate2, rate_5g, mode_5g, pwrlvl_5g, ch_5g, loss_5g)


    CMW1.close()
    UART1.close()