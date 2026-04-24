from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
# from aicintf.gpib import *
from toolkit.PXA import *
from MsPFM.ms_wf import *


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

def meas_fsq(pxa):
    # tt = pxa.get_peak_mark()
    tt = pxa.get_peak_mark_until_idle()
    mark_pwr = str(round(float(tt[1]), 2))
    mark_freq = str(round(float(tt[0]) / 1000000, 2))
    return mark_pwr, mark_freq

def set_auto_ref_pwr(fsqx):
    # self.set_reflvl(30)
    time.sleep(1)
    pwr = fsqx.get_peak_mark()[1]
    if int(float(pwr))<30:
        fsqx.set_reflvl(int(float(pwr)) + 15)
        time.sleep(1)

def set_band(pxa,start,stop,loss):
    # pxa.set_reflvl(30)
    pxa.set_startfreq(start)
    pxa.set_stopfreq(stop)
    # pxa.set_auto_ref_pwr()
    pwr, freq = meas_fsq(pxa)
    pwr = round(float(pwr)+loss, 2)
    return str(pwr),freq

def mea_muti_band(pxa,freq,loss):
    # fsq_init(fsqx, 200, 2400)
    pxa.sa.write("*CLS")
    pwr02,freq02=set_band(pxa,0.03, freq-40,loss)
    pwr24,freq24=set_band(pxa,freq-40, freq+40,loss)
    pwr25,freq25=set_band(pxa,freq+40,  2*freq-80,loss)
    pwr48,freq48=set_band(pxa,2*freq-80, 2*freq+80,loss)
    pwr50,freq50=set_band(pxa,2*freq+80, 3*freq-120,loss)
    pwr72,freq72=set_band(pxa,3*freq-120, 3*freq+120,loss)
    pwr75,freq75=set_band(pxa,3*freq+120, 26000,loss)
    return pwr02,freq02,pwr24,freq24,pwr25,freq25,pwr48,freq48,\
           pwr50,freq50,pwr72,freq72,pwr75,freq75

def get_freq_by_ch(ch):
    # defalut unit : MHz
    if int(ch) < 15:
        freq = (2407 + 5 * int(ch))
    elif (int(ch) > 30) and (int(ch) < 170):
        freq = (5000 + 5 * int(ch))
    else:
        freq = int(ch)
    # self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq

if __name__ == "__main__":

    # a=['1','1\n1']
    # b = a[0].split('\n')[0]

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE.xlsx'
    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE5_0.xlsx'
    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE_sample2.xlsx'
    xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE_all_sample.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # csv_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\Tuner_swp_data_20250805.csv'
    csv_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\8819_extre_data_'+current_time+'.csv'
    temp = 40


    # # PXA_IP = "10.21.10.166"
    # PXA_IP = "10.21.10.166::hislip0"
    PXA_IP = "TCPIP0::10.21.10.127::hislip0::INSTR"
    pxa = PXA(PXA_IP)
    # # pxa.open_tcp(PXA_IP, 5025)
    # pxa.open_visa('TCPIP0', PXA_IP)
    # print(pxa.id_string())
    # pxa.connect_pxa()



    UARTX = Uart(4, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()


    tuner1 = tuner()
    UART1 = Uart(17, wr_mode=True)
    UART1.set_baudrate("9600")
    UART1.open()
    # tuner_init(tuner1, UARTX, freq)
    # tuner1.open(UART1)
    # tuner1.init_tune(UART1)
    # time.sleep(2)
    # tuner1.load_file(UART1, str(freq))
    # time.sleep(2)



    csv_header1 = "test_time, BoardNo, ANT, Temp, am, phase, BinVersion,freq, Channel, Rate, BandWidth, " \
                  "SetPwr, CMD, MsPwrAvg, MsEvmAvg, "
    fre_band = "Band1, (0.03 to fch-40), Band2, (fch-40 to fch+40), Band3, (fch+40 to 2fch-80), Band4, (2fch-80 to 2fch+80)," \
               "Band5, (2fch+80 to 3fch-120), Band6, (3fch-120 to 3fch+120),Band, 7(3fch+120 to 26)\n"
    csv_header = csv_header1 + fre_band
    with open(csv_path, "a+") as CSVFILE:
        if csv_header.endswith("\n"):
            CSVFILE.write(csv_header)
        else:
            CSVFILE.write(csv_header + "\n")

    UARTX.sendcmd("pwrmm 1")
    UARTX.sendcmd("setintv 500")

    table_lines = WF_MS_TABLE(xlsx_path).read()
    for linex in table_lines:
        db_line = WF_MS_LINE(linex)
        if db_line.enable() not in ["Y", "y", "YES", "yes"]:
            continue

        for setchx in db_line.l_setch_ucmd():
            ch = setchx.strip().split(" ")[1]
            freq = get_freq_by_ch(ch)

            # tuner_init(tuner1, UART1, freq)
            tuner1.load_file(UART1, str(freq))
            time.sleep(0.5)


            # Uart start
            # UARTX.sendcmd("settx 1")

            UARTX.sendcmd(db_line.setrate_ucmd())
            UARTX.sendcmd(db_line.setbw_ucmd())
            UARTX.sendcmd(db_line.setlen_ucmd())
            rate = " ".join(db_line.setrate_ucmd().strip().split(" ")[1:])
            bw = " ".join(db_line.setbw_ucmd().strip().split(" ")[1:])
            len_set = " ".join(db_line.setlen_ucmd().strip().split(" ")[1:])

            wlan_standard = "11ax"
            if rate.strip().split(" ")[0] == "5":
                wlan_standard = "11ax"
            elif rate.strip().split(" ")[0] == "4":
                wlan_standard = "11ac"
            elif rate.strip().split(" ")[0] == "2":
                wlan_standard = "11n"
            elif rate.strip().split(" ")[0] == "0":
                if rate.strip().split(" ")[1] == "3":
                    wlan_standard = "11b"
                else:
                    wlan_standard = "11g"

            # pxa.set_wlan_freq_by_ch(ch)
            UARTX.sendcmd(setchx)
            time.sleep(2)

            for setpwrx in db_line.l_setpwr_ucmd():
                setpwr = " ".join(setpwrx.strip().split(" ")[1:])
                UARTX.sendcmd(setpwrx)

                cmdx = ""
                # print(db_line.l_uartcmd())
                try:
                    if db_line.l_uartcmd() is not None:
                        for u_cmdx in db_line.l_uartcmd():
                            cmdx = cmdx + UARTX.sendcmd(u_cmdx)
                            # print(cmdx)
                except:
                    cmdx = "ERROR"

                for key_str in [",", "\n", "\r", "aic>"]:
                    cmdx = cmdx.replace(key_str, " ")

                intv = 15
                # for am in range(9, -1, -1):
                for am in range(0, -1, -1):
                    # s=45
                    # a=int(float(s/am))
                    ampt = round((am / 10), 1)
                    if ampt == 0.0:
                        intv = 360
                    elif (ampt > 0) & (ampt <= 0.2):
                        # intv = 40
                        intv = 360
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

                        tuner1.set_tune(UART1, ampt, unphase)

                        UARTX.sendcmd("settx 1")
                        # b = tuner1.query_gamma(UART1)
                        # c = tuner1.query_postion(UART1)
                        # # print(c)
                        # print(b)
                        # values = b.strip().split(',')
                        # setAmp = float(values[1])  # 第二个值 (0.000)
                        # setPh = float(values[2])

                        # UART2.sendcmd("tone_on 01 1 1ff f")
                        time.sleep(2)

                        # tuner end
                        pxa.set_wlan_evm_meas()
                        pxa.set_wlan_standard(wlan_standard, bw)
                        pxa.set_cfreq(freq)


                        # # if rate.strip().split(" ")[1] == "3":
                        # if wlan_standard == "11b":
                        #     pxa.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 1')
                        #     time.sleep(0.4)
                        #     pxa.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 0')
                        #     pxa.sa.write(':SENS:EVM:AVER:STAT 1')

                            # pxa.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 0')
                        # else:
                        #     pxa.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 0')


                        # all_res = pxa.wlan_meas_result(wlan_standard)
                        all_res = pxa.wlan_meas_result_until_idle(wlan_standard)

                        # pxa.sa.write(':SENS:RAD:STAN:WLAN:DET:AUTO 0')

                        if len(all_res) < 10:
                            pxa.print_red('*********evm error***********')

                        # time.sleep(2)
                        ms_pwr, ms_evm_avg, ms_evm_peak = pxa.get_pwr_evm_by_stand(db_line, wlan_standard, all_res)

                        print('pwr: ', ms_pwr, '        evm: ', ms_evm_avg)

                        # SAN
                        pxa.set_SAN_meas()
                        pxa.set_reflvl(30)
                        pxa.set_rb(1)
                        pxa.set_vb(3)
                        time.sleep(0.1)
                        loss = 0
                        pwr02, freq02, pwr24, freq24, pwr25, freq25, pwr48, freq48, pwr50, freq50, \
                        pwr72, freq72, pwr75, freq75 = mea_muti_band(pxa, freq, loss)


                        # pxa.set_wlan_evm_meas
                        test_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

                        results = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                            test_time, db_line.boardno(), db_line.ant(), temp, ampt, unphase, db_line.binversion(), freq,
                            ch, rate, bw, setpwr, cmdx, ms_pwr, ms_evm_avg,
                            pwr02, freq02, pwr24, freq24, pwr25, freq25, pwr48, freq48, pwr50, freq50, pwr72, freq72, pwr75, freq75)

                        UARTX.sendcmd("settx 0")
                        time.sleep(0.2)


                        with open(csv_path, "a+") as CSVFILE:
                            if results.endswith("\n"):
                                CSVFILE.write(results)
                            else:
                                CSVFILE.write(results + "\n")
                        # self.CSVX.write_append_line(results)
                        print(results)

                        end_time = time.time()  # 记录结束时间
                        elapsed_time = end_time - start_time  # 计算耗时

                        print(f"code spand : {elapsed_time:.4f} s")  # 保留4位小数




