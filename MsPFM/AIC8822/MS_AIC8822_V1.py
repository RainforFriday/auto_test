import os
import sys
import openpyxl

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from MsPFM.csv import *
from MsPFM.GlobalVar import *
global_create()
from MsPFM.wf_ms import *


def MS_AIC8822():
    csv_path = "./MsDatas/AIC8822_WF_MEASURE_TABLE_20240627_V2.csv"
    xlsx_path = "./MsTables/WF_MEASURE_TABLE_20240627_V2.xlsx"

    CSVX = CSV(csv_path)
    csv_header = "Channel, Rate, BandWidth, Length, SetPwr, MsPwrAvg, MsEvmAvg\n"
    CSVX.write_append_line(csv_header)

    UARTX = Uart(8)
    UARTX.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    GX.set_value("UARTX", UARTX)
    GX.set_value("CSVX", CSVX)
    GX.set_value("CMPX", CMPX)

    MS = WF_MS(xlsx_path)
    MS.wf_ms_table()


if __name__ == "__main__":
    MS_AIC8822()