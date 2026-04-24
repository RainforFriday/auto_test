from aicintf.agilent import *
from pyinstr.rs.Tuner import *
from pyinstr.rs.cmw import *
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
    tt = pxa.get_peak_mark()
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
    pxa.write("*CLS")
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
    # self.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq

if __name__ == "__main__":

    # a=['1','1\n1']
    # b = a[0].split('\n')[0]

    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE.xlsx'
    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE5_0.xlsx'
    # xlsx_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\table\Extre_TABLE_sample2.xlsx'

    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    # csv_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\extreme_condition\data\Tuner_swp_data_20250805.csv'
    csv_path = r'D:\Aic8800\Code\AIC_TEST\aic8819\aic8819_tunnertest\pwr_consumption\data\8819_pwr_cur_'+current_time+'.csv'

    setpwr = 18
    ch = 7
    freq = get_freq_by_ch(ch)
    board = 5
    bin_version ='testmode_8819h_820_high_apc'



    UARTX = Uart(8, wr_mode=True)
    UARTX.set_baudrate("921600")
    UARTX.open()

    # PXA_IP = "10.21.10.166"
    # pxa = PXA()
    # pxa.open_tcp(PXA_IP, 5025)
    # print(pxa.id_string())




    tuner1 = tuner()
    UART1 = Uart(17, wr_mode=True)
    UART1.set_baudrate("9600")

    UART1.open()
    # tuner_init(tuner1, UARTX, freq)
    tuner1.open(UART1)
    tuner1.init_tune(UART1)
    time.sleep(2)
    tuner1.load_file(UART1, str(freq))
    time.sleep(2)

    host = "10.21.10.124"
    port = 5025
    CMW1 = CMW()
    CMW1.open_tcp(host, port)
    print(CMW1.id_string())



    Agilent = agilent(6)
    Agilent.open()

    # UARTX.sendcmd("pwrmm 1")
    # UARTX.sendcmd("setintv 500")



    csv_header1 = "test_time, BoardNo, am, phase, BinVersion,freq, Channel, " \
                  "SetPwr, "
    fre_band = "pwr, freq, Current\n"
    csv_header = csv_header1 + fre_band
    with open(csv_path, "a+") as CSVFILE:
        if csv_header.endswith("\n"):
            CSVFILE.write(csv_header)
        else:
            CSVFILE.write(csv_header + "\n")




    # tuner_init(tuner1, UART1, freq)
    tuner1.load_file(UART1, str(freq))
    time.sleep(2)

    # for tone_id in [0,1]:
    #     intv = 15
    for am in range(9, -1, -1):
    # for am in range(1, -1, -1):
        ampt = round((am / 10), 1)
        if ampt == 0.0:
            intv = 360
        elif (ampt > 0) & (ampt <= 0.2):
            intv = 40
            # intv = 360
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

            UARTX.sendcmd("tone_on 4 aff 07")
            time.sleep(1)

            CMW1.write('INITiate:GPRF:MEAS:SPECtrum')
            time.sleep(2)
            ms_list = CMW1.query('FETCh:GPRF:MEAS:SPECtrum:REFMarker:SPEak? MAXPeak, AVERage').strip().split(',')
            ms_pwr = str(round(float(ms_list[2]), 2))
            ms_freq = str(round(float(ms_list[1]) / 1000000, 2))

            print('pwr: ', ms_pwr, '        freq: ', ms_freq)

            current_readings = []
            for _ in range(1):
                currs = float(Agilent.meas_curr1().strip()) * 1000
                time.sleep(0.2)
                current_readings.append(currs)
                print(f"第{_ + 1}次测量值：{currs:.2f} mA")
            curr = round(sum(current_readings) / len(current_readings), 2)

            # pxa.set_wlan_evm_meas
            test_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

            results = "{},{},{},{},{},{},{},{},{},{},{}".format(
                test_time, board, ampt, unphase,bin_version, freq,
                ch,setpwr, ms_pwr, ms_freq, curr
            )

            UARTX.sendcmd("tone_off")

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


    # UART2.sendcmd("tone_on 01 1 1ff f")
    time.sleep(1)

    # finish
    UARTX.close()
    CMW1.close()
    UART1.close()
    # Agilent.OUTP_OFF()
    Agilent.close()