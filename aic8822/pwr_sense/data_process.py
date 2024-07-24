# this scripts is used for data process
# curve fitting

import os
import sys
import matplotlib.pyplot as plt
import numpy as np


class PWRCSV:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def read_csv_by_ch(self, ch):
        data_ch = []
        with open(self.csv_path, "r") as CSVX:
            data = CSVX.readlines()
        for data_cell in data:
            if data_cell.strip().split(",")[0] == str(ch):
                data_ch.append(data_cell)
        return data_ch

    def l_dig_pwr_index_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch(ch):
            datax.append(int(data_cell.strip().split(",")[1]))
        return datax

    def l_msadc_pwrmw_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch(ch):
            datax.append(float(data_cell.strip().split(",")[5]))
        return datax

    def l_msadc_pwrdbm_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch(ch):
            datax.append(float(data_cell.strip().split(",")[3]))
        return datax

    def l_instr_pwrmw_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch(ch):
            datax.append(float(data_cell.strip().split(",")[6]))
        return datax

    def l_instr_pwrdbm_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch(ch):
            datax.append(float(data_cell.strip().split(",")[4]))
        return datax

    def l_msadc_vs_instr_min_max(self, ch, msadc_mw_min = 10.0, msadc_mw_max = 100.0):
        l_msadc_mw = []
        l_instr_mw = []
        for data_cell in self.read_csv_by_ch(ch):
            # print(data_cell)
            msadc_mw = float(data_cell.strip().split(",")[5])
            instr_mw = float(data_cell.strip().split(",")[6])
            # print("{},{}".format(msadc_mw, instr_mw))
            if (msadc_mw > msadc_mw_min) and (msadc_mw < msadc_mw_max):
                l_msadc_mw.append(msadc_mw)
                l_instr_mw.append(instr_mw)
        return [l_msadc_mw, l_instr_mw]


def curve_fitting(l_msadc_mw, l_instr_mw):
    coefficient = np.polyfit(l_msadc_mw, l_instr_mw, 2)
    print(coefficient)


if __name__ == "__main__":
    HB = True
    if HB:
        csv_path = "./data/20240722/pwr_sense_data_HB1_CALED_20240722_1750.csv"
        CSVX = PWRCSV(csv_path)
        for chx in [42, 58, 106, 122, 138, 155]:
            xxx = CSVX.l_msadc_vs_instr_min_max(chx, 10, 500)
            curve_fitting(xxx[0], xxx[1])

    LB = False
    if LB:
        csv_path = "./data/20240719/pwr_sense_data_LB1_CALED_20240719_1816.csv"
        CSVX = PWRCSV(csv_path)
        for chx in [1, 7, 13]:
            xxx = CSVX.l_msadc_vs_instr_min_max(chx, 10, 1000)
            curve_fitting(xxx[0], xxx[1])


    """
    l_msadc = LBCSV.l_msadc_pwrmw_by_ch(CHX)
    l_instr = LBCSV.l_instr_pwrmw_by_ch(CHX)

    l_instr_div_msadc = []
    for i in range(len(l_msadc)):
        l_instr_div_msadc.append(l_instr[i]/l_msadc[i])
    print(l_instr_div_msadc)

    xxx = curve_fitting(l_msadc, l_instr_div_msadc)
    print(xxx)

    """

    """
    for CHX in [1, 7, 13]:
        l_msadc = LBCSV.l_msadc_pwrmw_by_ch(CHX)
        l_instr = LBCSV.l_instr_pwrmw_by_ch(CHX)
        # print(l_msadc)
        # print(l_instr)
        print(curve_fitting(l_msadc, l_instr))
    """