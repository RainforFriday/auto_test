# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: ampm_cal.py
@time: 2021/8/17 18:57
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

PLEN = 10  # paramter len 10 data each parameter
PNUM = 17  #
PM_TABLE = []  # pm_p0, pm_p1,...,pm_p16, total 17 parameter


def ampm_table_degree2bin(pm_talbe_degree):
    # degree [0：360]---->[10'b0000000000,...,10'b1111111111]
    # each bit mean: 360/(2^10-1)
    pm_talbe_bin = []
    for phase_degree in pm_talbe_degree:
        # make sure phase degree in range [0,360)
        phase_degree = phase_degree % 360
        num = round(phase_degree/(360.0/(pow(2, PLEN)-1)))
        # pm_talbe_bin.append('{:010b}'.format(num))
        pm_talbe_bin.append(num)
    return pm_talbe_bin


def curve_1order(xy1, xy2):
    # 1 order insert value
    # xy1 = [x1, y1]
    # xy2 = [x2, y2]
    # y = k1*x + b1
    k1 = (xy2[1] - xy1[1])/(xy2[0] - xy1[0])
    b1 = xy1[1] - k1*xy1[0]
    return [k1, b1]


def ampm_curve_1order(xy_list, index):
    # xy_list =[[x0,y0],[x1,y1],[x2,y2],...]
    # x0,x1,...,xn   in (0,16)
    # y0,y1,...,yn   in degree unit
    for num in range(len(xy_list)-1):
        if (index >= xy_list[num][0]) and (index <= xy_list[num+1][0]):
            [k0, b0] = curve_1order(xy_list[num], xy_list[num+1])
            degree_value = k0 * index + b0
    return degree_value


def lagrange(xy_list, index):
    # n order lagrange insert value
    # xy_list = [[x0, y0], [x1, y1], [x2, y2], ..., [xn, yn]]   n>=3
    # y = an*x^n+an-1*x^(n-1)+...+a0
    yvalue = 0
    for i in range(len(xy_list)):
        t = xy_list[i][1]
        for j in range(len(xy_list)):
            if i != j:
                t = t * (index - xy_list[j][0])
                t = t / (xy_list[i][0] - xy_list[j][0])
        yvalue = yvalue + t
    return yvalue


def ampm_curve_Norder(xy_list, index_list):
    yvalue = []
    for index in index_list:
        # yvalue.append(lagrange(xy_list, index))
        yvalue.append(ampm_curve_1order(xy_list, index))
    # print(yvalue)
    return yvalue


def ampm_offset(phase_list, offset=0.0):
    phase_data = []
    for phase_value in phase_list:
        phase_data.append(phase_value+offset)
    return phase_data


def cure_plt(x_list, y_list):
    plt.plot(x_list, y_list, ls="-", lw=2)
    plt.xlabel("INDEX")
    plt.ylabel("PHASE (Degree)")
    plt.show()


def ampm_table_create(xy_list, offset):
    index_list = [i for i in range(17)]
    phase = ampm_curve_Norder(xy_list, index_list)
    phase_offset = ampm_offset(phase, offset)
    return ampm_table_degree2bin(phase_offset)


if __name__ == "__main__":
    # xy_list = [[0, 0], [16, 0]]
    # xy_list = [[0, 0], [7, 0], [16, 10]]
    xy_list = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [12, 3], [16, 10]]
    index_list = [i for i in range(17)]
    # aaa = []
    # for i in range(64):
    #    aaa.append(i*0.25)
    # y = ampm_curve_Norder(xy_list, aaa)
    phase_reg_dec = ampm_table_create(xy_list, 0)
    cure_plt(index_list, phase_reg_dec)
