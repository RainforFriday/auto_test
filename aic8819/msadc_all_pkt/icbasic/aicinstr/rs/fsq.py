from aicinstr.rs.genericinstrument import *

__version__ = "v0.1"


class FSQ(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()

    def set_analyzer_mode(self):
        self.write("INST:SEL SAN")
        return True

    def set_mode(self, mode="SWE"):
        self.write("FREQ:MODE {}".format(mode))
        return True

    def get_mode(self):
        return self.query("FREQ:MODE?")

    def set_cfreq(self, cfreq):  # cfreq unit is MHz
        self.write("FREQ:CENT {}MHZ".format(cfreq))
        return True

    def get_cfreq(self):
        return self.query("FREQ:CENT?")

    def set_startfreq(self, sfreq):  # startfreq unit is MHz
        self.write("FREQ:START {}MHz".format(sfreq))
        return True

    def set_stopfreq(self, sfreq):  # sfreq unit is MHz
        self.write("FREQ:STOP {}MHz".format(sfreq))
        return True

    def set_rb(self, rb):
        self.write("BAND {}MHz".format(rb))
        return True

    def get_rb(self):
        return self.query("BAND?")

    def set_rb_ratio(self, rat=0.1):  # rat = BW/SPAN
        self.write("BAND:RAT {}".format(rat))
        return True

    def set_vb(self, vb):  # vb = 1HZ --- 30MHz , unit MHz
        self.write("BAND:VID {}MHz".format(vb))
        return True

    def get_vb(self):
        return self.query("BAND:VID?")

    def set_vb_rat(self, rat):  # rat = VideoBandwidth/SPAN
        self.write("BAND:VID:RAT {}".format(rat))
        return True

    def set_span(self, span):   # span unit is MHz
        self.write("FREQ:SPAN {}MHz".format(span))
        return True

    def get_span(self):
        return self.query("FREQ:SPAN?")

    def set_reflvl(self, reflvl):
        self.write("DISP:WIND:TRAC:Y:RLEV {}dBm".format(reflvl))
        return True

    def get_reflvl(self):
        pass
        # return self.write("WIND:TRAC:Y:RLEV?")

    def meas_stat(self):
        pass

    def meas_start(self):
        pass

    def meas_abort(self):
        pass

    def meas_stop(self, unit_no=1):
        pass

    def pwroff(self):
        pass

    def sweep_ctrl(self):
        pass

    def get_trace(self):
        pass

    def show(self):
        pass

    def set_param(self, cfreq, span=100, rb=100, vb=30):
        pass

    def get_peak_mark(self):
        self.write("CALC:MARK:MAX")
        self.write("INIT;*WAI")
        return [self.query("CALC:MARK:X?"), self.query("CALC:MARK:Y?")]

    def get_peak_mark_avg(self, N=10):
        x = 0
        y = 0
        num = 0
        for i in range(int(N)):
            # x = x + self.get_peak_mark()[0]
            num = num + 1
            y = y + float(self.get_peak_mark()[1])
            y_avg = y/float(num)
            if abs(float(self.get_peak_mark()[1]) - y_avg) > 0.5:
                print("get mark peak error")
        return [x, y/float(N)]

    def get_mark(self):
        xx = self.query("CALC:MARK:X?")
        yy = self.query("CALC:MARK:Y?")
        return [xx, yy]

    def clear_mark(self):
        self.write("CALC:MARK:AOFF")
        return True

    # search peaks in current span
    def pk_search(self, th=-60, pk_excursion=6):
        pass

    def pk_scan(self, th=-60, pk_excursion=6, start_freq=1, end_freq=6000, store_path='null'):
        pass

    def meas_pwr(self, reflvl, cfreq, span, rb, bdwdth_mhz, vavg_no=20, vb=30):
        pass

    # flt_bwdth is half filter bandwidth,unit is MHz
    def fltn_pwr(self, tone_freq, reflvl, flt_bwdth=8):
        pass

    def reflvl_srch(self, tone_freq, ini_reflvl=0):
        pass

    def pk_detect(self):
        pass

    def get_result(self, name):
        pass


if __name__ == "__main__":
    host = "10.21.10.180"
    port = 5025
    FSQ1 = FSQ()
    FSQ1.open_tcp(host, port)
    FSQ1.set_analyzer_mode()
    print(FSQ1.get_mode())
    FSQ1.set_cfreq(2412)
    print(FSQ1.get_cfreq())
    FSQ1.set_span(20)
    print(FSQ1.get_span())
    FSQ1.set_reflvl(10)
    print(FSQ1.get_reflvl())
    FSQ1.set_rb(0.05)
    print(FSQ1.get_rb())
    for i in range(1):
        FSQ1.get_peak_mark()
        mark = FSQ1.get_mark()
        print(mark)

