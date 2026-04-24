from pyinstr.rs.Tuner import *
# from pyinstr.rs.cmw import *
# from pyinstr.rs.fsq import *
# from aicintf.gpib import *
# from toolkit.PXA import *
from icbasic.toolkit.util import *
from icbasic.toolkit.PXA import *
from icbasic.toolkit.CMP180vs import *

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
    pxa.set_reflvl(16)
    pxa.set_rb(1)
    pxa.set_vb(3)
    # tt = pxa.get_peak_mark()
    tt = pxa.get_peak_mark_until_idle()
    # mark_pwr = str(round(float(tt[1]), 2))
    # mark_freq = str(round(float(tt[0]) / 1000000, 2))
    return tt[1], tt[0]

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
    return pwr, freq

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


def tone_off():
    UARTX.sendcmd("w 40344088 0150004d")

def tone_on():
    UARTX.sendcmd("w 40344088 0170004d")

def pll_test_on():
    UARTX.sendcmd("w 40344008 8")


def tone_on_2G4():
    UARTX.sendcmd("tone_on 4 3ff 1f")

def tone_on_5G():
    UARTX.sendcmd("tone_on 4 3ff 2f")


if __name__ == "__main__":

    loss = 0

    # xlsx_path = r'.\table\Extre_TABLE.xlsx'
    xlsx_path = r'.\table\Extre_TABLE_sample.xlsx'
    # xlsx_path = r'.\table\Extre_TABLE_all_sample.xlsx'
    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    file_path = r'.\data\8819_extre_data_' + current_time + '.xlsx'

    temp = 85



    PXA_IP = "TCPIP0::10.21.12.195::hislip0::INSTR"
    pxa = PXA(PXA_IP)
    pxa.set_Det()
    pxa.set_att(40)
    pxa.set_reflvl(30)
    pxa.set_rb(0.1)
    pxa.set_vb(0.3)
    pxa.set_span(60)
    time.sleep(1)


    UARTX = Uart(4, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    bin_file = "testmode20_2025_1205_1950.bin"
    # bin_file = "testmode_8822_924_6e_temp.bin"

    # # once
    # UARTX.sendcmd('reboot')
    # time.sleep(2)
    # bin_file_path = './bin/'+bin_file
    # load_bin_X16(UARTX, bin_file_path)
    # time.sleep(1)




    tuner1 = tuner()
    UART1 = Uart(7, wr_mode=True)
    UART1.set_baudrate("9600")
    UART1.open()
    # tuner_init(tuner1, UARTX, freq)
    # tuner1.open(UART1)
    # tuner1.init_tune(UART1)
    # time.sleep(2)
    # tuner1.load_file(UART1, str(freq))
    # time.sleep(2)


    data_dict = {}
    # pxa.set_Det()
    # pxa.sa.write(":SENSe:POWer:RF:ATTenuation 26")




    table_lines = WF_MS_TABLE(xlsx_path).read()
    for linex in table_lines:
        db_line = WF_MS_LINE(linex)
        if db_line.enable() not in ["Y", "y", "YES", "yes"]:
            continue

        for setchx in db_line.l_setch_ucmd():
            ch = setchx.strip().split(" ")[1]
            freq = get_freq_by_ch(ch)
            print_red(f'ch: {ch}')

            tuner_init(tuner1, UART1, freq)

            UARTX.sendcmd(setchx)
            time.sleep(2)

            pxa.set_cfreq(freq)

            if int(ch)> 15:
                tone_on_5G()
            else:
                tone_on_2G4()
            # UARTX.sendcmd('tone_on 1 3ff 1f')
            pll_test_on()
            # UARTX.sendcmd('w 40344008 8')
            time.sleep(0.5)
            tone_off()

            for setpwrx in db_line.l_setpwr_ucmd():
                intv = 15
                # total：
                # for am in range(9, -1, -1):
                # for am in range(3, -1, -1):
                for am in range(9, 8, -1):
                    ampt = round((am / 10), 1)
                    if ampt == 0.0:
                        intv = 360
                    elif (ampt > 0) & (ampt <= 0.2):
                        intv = 40
                    elif (ampt >= 0.3) & (ampt < 0.5):
                        intv = 30
                        # intv = 10
                    elif (ampt >= 0.5) & (ampt <= 0.7):
                        intv = 20
                    else:
                        # intv = 15
                        intv = 180
                    # print(ampt)
                    for unphase in range(-180, 178, intv):
                    # for unphase in range(-10, 50, intv):
                        start_time = time.time()
                        # print(unphase)
                        if ampt == 0.0:
                            unphase = 0

                        tuner1.set_tune(UART1, ampt, unphase)

                        time.sleep(2)


                        max_retries = 3
                        for attempt in range(max_retries):
                            # pxa.set_auto_ref_pwr()
                            pxa.sa.write('TRAC1:TYPE WRIT')
                            pxa.sa.write('TRAC1:TYPE MAXH')
                            tone_on()
                            tt = pxa.get_peak_mark_until_idle()
                            tone_off()
                            # pxa.get_peak_mark()

                            if float(tt[0]) - freq < 1:
                                break
                            print_red(f"failed, again!")
                            tone_off()
                            time.sleep(1)
                            tone_on()

                            # UARTX.sendcmd(setchx)
                            # time.sleep(1.5)
                            # CMPX.wlan_meas_abort()
                            # UARTX.sendcmd(setpwrx)
                            # UARTX.sendcmd("settx 1")

                        # ms_pwr = float(ms_pwr) + loss

                        print('pwr: ', tt[1])
                        # pxa.set_wlan_evm_meas
                        # test_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
                        test_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
                        data_dict['test_time'] = test_time
                        data_dict['bin'] = bin_file
                        # data_dict['boardNo'] = db_line.boardno()
                        # data_dict['temp'] = temp
                        data_dict['freq'] = freq
                        data_dict['channel'] = ch

                        # data_dict['cmd'] = cmdx
                        data_dict['am'] = ampt
                        data_dict['phase'] = unphase
                        data_dict['PwrAvg'] = tt[1]


                        # UARTX.sendcmd("tone_off")
                        time.sleep(0.2)

                        print("数据行：", data_dict)
                        save_results(data_dict, file_path)

                        end_time = time.time()  # 记录结束时间
                        elapsed_time = end_time - start_time  # 计算耗时
                        print(f"code spand : {elapsed_time:.4f} s")  # 保留4位小数
            tone_off()

    # CMPX.wlan_meas_abort()
    tone_off()
    UARTX.close()

