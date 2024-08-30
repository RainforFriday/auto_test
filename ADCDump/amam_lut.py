# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: amam_lut.py
@time: 2021/8/25 10:10
"""

import os
import sys
import math
import matplotlib.pyplot as plt


def curve_1order_get_y(x0, y0, x1, y1, xin):
    k = (y1 - y0)/(x1 - x0)
    b = y0 - k * x0
    return k*xin+b


def curve_1order_get_x(x0, y0, x1, y1, yin):
    k = (y1 - y0)/(x1 - x0)
    b = y0 - k * x0
    return (yin - b)/k


def get_yvalue_from_list(x_list, y_list, xin):
    for i in range(len(x_list)-1):
        if (xin >= x_list[i]) and (xin < x_list[i+1]):
            yout = curve_1order_get_y(x_list[i], y_list[i], x_list[i+1], y_list[i+1], xin)
        if xin > x_list[-1]:
            yout = y_list[-1]
    return yout


def get_xvalue_from_list(x_list, y_list, yin):
    for i in range(len(x_list)-1):
        if (yin >= y_list[i]) and (yin < y_list[i+1]):
            xout = curve_1order_get_x(x_list[i], y_list[i], x_list[i+1], y_list[i+1], yin)
        if yin > y_list[-1]:
            xout = x_list[-1]
    return xout


def lut_x2x(x_list, y_list, xin):
    # y = k*x + b
    # y_list = k * log10(x_list) + b

    # 1 get k, b

    # 2 caculate ideal y
    y_ideal = k * math.log10(xin) +b

    # 3 find real y
    # y_real = get_yvalue_from_list(x_list, y_list, xin)

    # 4 check y_ideal-y_real
    # yerror = abs(y_ideal - y_real)

    # 5 get xvalue
    return get_xvalue_from_list(x_list, y_list, y_ideal)


def cure_plt(x_list, y_list):
    plt.plot(x_list, y_list, ls="-", lw=2)
    plt.xlabel("XLABLE")
    plt.ylabel("YLABLE")
    plt.show()


if __name__ == "__main__":
    x_list = []
    y_list = []
    amam_in = [0]
    amam_out = [0]
    for i in range(256, 4095, 256):
        amam_in.append(i)
        amam_out.append(lut_x2x(x_list, y_list, i))
    amam_in.append(4095)
    amam_out.append(4095)
    cure_plt(amam_in, amam_out)