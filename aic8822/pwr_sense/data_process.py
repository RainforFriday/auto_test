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

def curve_fitting(l_msadc, l_instr):
    coefficient = np.polyfit(l_msadc, l_instr, 1)
    return coefficient


if __name__ == "__main__":
    csv_path = "./data/20240719/pwr_sense_data_LB_20240719_1528.csv"
    LBCSV = PWRCSV(csv_path)

    # y=1.211*x - 20.571

    for CHX in [1, 7, 13]:
        l_msadc = LBCSV.l_msadc_pwrmw_by_ch(CHX)
        l_instr = LBCSV.l_instr_pwrmw_by_ch(CHX)
        print(l_msadc)
        print(l_instr)
        print(curve_fitting(l_msadc, l_instr))
