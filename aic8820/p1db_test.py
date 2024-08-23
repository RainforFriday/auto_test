from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
import os
import sys
from aic8820.csv import *


if __name__ == "__main__":
    csv_name = "./data/aic8820_tone_pwr_24g_20240812_1156.csv"

    UARTc = Uart(7)
    UARTc.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180(1)
    CMPX.open_tcp(host, port)

    CSVX = CSV(csv_name)

    for dig_pwr in range(64, 4096, 64):  # 640
        dig_pwr_hex_str = hex(dig_pwr).split("0x")[-1]

        # UARTc.sendcmd("tone_on 1 {} f".format(dig_pwr_hex_str))
        UARTc.sendcmd("tone_on 1 {} d".format(dig_pwr_hex_str))
        time.sleep(1)
        CMPX.fsp_auto_enpwr()
        CMPX.fsp_on()
        pwr_cmp180 = CMPX.fsp_peak_pwr()
        UARTc.sendcmd("tone_off")
        CMPX.fsp_off()
        CSVX.write_append_line("{},{}\n".format(dig_pwr, pwr_cmp180))