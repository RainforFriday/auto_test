# this scripts is used for data process
# curve fitting

import os
import sys
import matplotlib.pyplot as plt
import numpy as np


class PWRCSV:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def read_csv_by_ch_ant(self, ch, ant):
        data_ch = []
        with open(self.csv_path, "r") as CSVX:
            data = CSVX.readlines()
        for data_cell in data:
            if (data_cell.strip().split(",")[1] == str(ch)) and (data_cell.strip().split(",")[0] == str(ant)):
                data_ch.append(data_cell)
        return data_ch

    def l_dig_pwr_index_by_ch(self, ch, ant):
        datax = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            datax.append(int(data_cell.strip().split(",")[2]))
        return datax

    def l_msadc_pwrmw_by_ch(self, ch, ant):
        datax = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            datax.append(float(data_cell.strip().split(",")[6]))
        return datax

    def l_msadc_pwrdbm_by_ch(self, ch, ant):
        datax = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            datax.append(float(data_cell.strip().split(",")[4]))
        return datax

    def l_instr_pwrmw_by_ch(self, ch, ant):
        datax = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            datax.append(float(data_cell.strip().split(",")[7]))
        return datax

    def l_instr_pwrdbm_by_ch(self, ch):
        datax = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            datax.append(float(data_cell.strip().split(",")[5]))
        return datax

    def l_msadc_vs_instr_min_max(self, ch, ant, msadc_mw_min = 10.0, msadc_mw_max = 100.0):
        l_msadc_mw = []
        l_instr_mw = []
        for data_cell in self.read_csv_by_ch_ant(ch, ant):
            # print(data_cell)
            msadc_mw = float(data_cell.strip().split(",")[6])
            instr_mw = float(data_cell.strip().split(",")[7])
            # print("{},{}".format(msadc_mw, instr_mw))
            if (msadc_mw > msadc_mw_min) and (msadc_mw < msadc_mw_max):
                l_msadc_mw.append(msadc_mw)
                l_instr_mw.append(instr_mw)
        # print([l_msadc_mw, l_instr_mw])
        return [l_msadc_mw, l_instr_mw]


def curve_fitting(l_msadc_mw, l_instr_mw):
    coefficient = np.polyfit(l_msadc_mw, l_instr_mw, 2)
    print(coefficient)


if __name__ == "__main__":
    HB = True
    if HB:
        # csv_path = "./data/20240722/pwr_sense_data_HB1_CALED_20240722_1750.csv"
        csv_path1 = "./data/20240726/NO1_pwr_sense_data_20240726_1646.csv"
        csv_path2 = "./data/20240726/NO2_pwr_sense_data_20240726_1646.csv"
        csv_path3 = "./data/20240726/NO6_pwr_sense_data_20240726_1646.csv"
        csv_path4 = "./data/20240726/NREF_pwr_sense_data_20240726_1646.csv"

        csv_pathx = [csv_path1, csv_path2, csv_path3, csv_path4]
        # ant = "0"

        for ant in ["0", "1"]:
            print("ANT : {}".format(ant))
            for csv_path in csv_pathx:
                CSVX = PWRCSV(csv_path)
                for chx in ["155"]:  #[42, 58, 106, 122, 138, 155]:
                    # print("CHANNEL : {}".format(chx))
                    xxx = CSVX.l_msadc_vs_instr_min_max(chx, ant, 10, 500)
                    curve_fitting(xxx[0], xxx[1])

    LB = False
    if LB:
        csv_path = "./data/20240719/pwr_sense_data_LB1_CALED_20240719_1816.csv"
        CSVX = PWRCSV(csv_path)
        for chx in [1, 7, 13]:
            xxx = CSVX.l_msadc_vs_instr_min_max(chx, 5, 1000)
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


# CH42 : 4.4E-4*x^2 + 8E-1*X + 1.5
# CH58 : 3.3E-4*x^2 + 7E-1*X + 1.5
# CH106 : 4.4E-4*x^2 + 8E-1*X + 0
# CH122 : 4.0E-4*x^2 + 8E-1*X + 0
# CH138 : 6.0E-4*x^2 + 1*X + 0
# CH155 : 5.0E-4*x^2 + 1*X + 0


