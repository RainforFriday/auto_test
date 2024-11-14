import os
import sys
import openpyxl

from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf.uart import *
from MsPFM.csv import *
from MsPFM.GlobalVar import *
global_create()
from MsPFM.ms_wf import *


def MSAIC(COMNUM, xlsx_path, csv_path):
    # csv_path = "./MsDatas/AIC8822_WF_MEASURE_DATA_20240628_V3.csv"
    # xlsx_path = "./MsTables/WF_MEASURE_TABLE_20240628_V3.xlsx"

    UARTX = Uart(COMNUM)
    UARTX.open()

    host = "10.21.10.200"
    port = 5025
    CMPX = CMP180()
    CMPX.open_tcp(host, port)

    CSVX = CSV(csv_path)

    GX.set_value("UARTX", UARTX)
    GX.set_value("CSVX", CSVX)
    GX.set_value("CMPX", CMPX)

    MS = WF_MS(xlsx_path)
    MS.wf_ms_table()


if __name__ == "__main__":
    COMNUM = 7

    # aic8820
    # xlsx_path = "./AIC8820/MsTables/WF_MEASURE_TABLE_20240821_11B_X0.xlsx"
    # csv_path = "./AIC8820/MsDatas/NO2_AIC8820D40L_11b_spwr_20240821_x1.csv"

    # aic8822
    xlsx_path = "./AIC8822/MsTables/20241022/WF_MEASURE_TABLE_LB_V1_20241022.xlsx"
    csv_path = "./AIC8822/MsDatas/20241022/WF_MEASURE_TABLE_20241022_1617.csv"

    MSAIC(COMNUM, xlsx_path, csv_path)
