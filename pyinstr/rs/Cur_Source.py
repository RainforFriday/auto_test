

from pyinstr.rs.genericinstrument import *

class keysight(GenericInstrument):
    def __init__(self):
        super(GenericInstrument, self).__init__()
        #self.tx_connector = ["RF1C", "RF1O", "RF2C"]

    def reset(self):
        self.write("*RST; *OPC?")

    def clear(self):
        self.write("*CLS; *OPC?")

    def meas(self):
        #self.write("CONF: VOLT:DC 1,0.0001")
        #self.write("TRIG: SOUR EXT")
        #self.write("INIT")
       # self.write("CONFigure:CONTinuity}")

        #self.write(" TRIG: SOUR EXT ")
        self.write("[SENSe:]VOLTage:{DC}:RANGe:AUTO?")
        time.sleep(0.5)
        return self.write("MEASure[:VOLTage]:{AC|DC}? [{<range>|AUTO|MIN|MAX|DEF} [, {<resolution>|MIN|MAX|DEF}]]")

    def close(self):
        self.write("SYSTem:LOCal")

if __name__ == "__main__":
    host = "10.21.10.192"
    port = 5025
    KEYSIGHT = keysight()
    KEYSIGHT.open_tcp(host, port)
    print(KEYSIGHT.id_string())
    time.sleep(0.5)
    KEYSIGHT.close()
    a=KEYSIGHT.meas()
    print(a)
    #print(b)
    KEYSIGHT.close()
