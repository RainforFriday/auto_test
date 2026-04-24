# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: regvalue.py
@time: 2020/5/29 15:48
"""

import os
import sys
sys.path.append("..")
from pybasic.hpnum import *


class RegValue(HpNum):
    def __init__(self, reg_value):
        super(RegValue, self).__init__(reg_value)
        self.value = reg_value

    def bin_len(self):
        return len(self.BIN)-2

    def bits_modify(self, bits_position, bits_value):
        """
        :param bits_position:  eg: "2:3"
        :param bits_value:   eg: 12
        :return:
        """
        len_value = self.bin_len()
        and_value = self.__bits_position_and__(len_value, bits_position)
        or_value = self.__bits_position_or__(bits_position, bits_value)
        return hex(int(self.DEC) & and_value | or_value)

    def __bits_position_check__(self, bits_position):
        if ":" in bits_position:
            if len(bits_position.split(":")) == 2:
                num_start = bits_position.split(":")[0]
                num_stop = bits_position.split(":")[1]
            else:
                wlogerror("bits_position input error")

    def __bits_position_len__(self, bits_position):
        if ":" in bits_position:
            num_start = int(bits_position.split(":")[0])
            num_stop = int(bits_position.split(":")[1])
            return abs(num_start - num_stop) + 1
        else:
            return 1

    def __bits_position_and__(self, t_len, bits_position):
        """
        :param t_len: 4
        :param bits_positon: 2:1
        :return: 0b1001
        """
        value = 0
        if ":" in bits_position:
            num_start = int(bits_position.split(":")[0])
            num_stop = int(bits_position.split(":")[1])
            for i in range(min(num_start, num_stop), max(num_start, num_stop)+1):
                value = value + 2**i
        else:
            value = 2**int(bits_position)
        # return bin((2**t_len-1) - value)
        return (2**t_len-1) - value

    def __bits_position_or__(self, bits_position, value):
        """
        :param bits_position:   2:1
        :param value: 2  , dec
        :return:  0b100
        """
        if ":" in bits_position:
            num_start = int(bits_position.split(":")[0])
            num_stop = int(bits_position.split(":")[1])
            if value > 2**(abs(num_start - num_stop) + 1) - 1:
                wlogerror("Input ERROR")
                mult = 0
            else:
                mult = 2**min(num_stop, num_start)
        else:
            if value > 1:
                wlogerror("Input ERROR")
                mult = 0
            else:
                mult = 2**int(bits_position)
        # return bin(value*mult)
        return value*mult


if __name__ == "__main__":
    num = "0b1001001011"
    regvalue1 = RegValue(num)
    # print(regvalue1.bin_len())
    # print(regvalue1.BIN)
    for i in range(0,8):
        print(regvalue1.bits_modify("4:2", i))
