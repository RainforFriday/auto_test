# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: uart.py
@time: 2020/5/29 13:14
"""

import os
import sys
from pyintf.com import *
from pyreg.regvalue import *


class Uart(COM):
    def __init__(self, com_port=3, wr_mode=False):
        super(Uart, self).__init__(com_port)
        if wr_mode:
            self.reg_w_cmd = "w"
            self.reg_r_cmd = "r"
        else:
            self.reg_w_cmd = "mw"
            self.reg_r_cmd = "md"

    def reg_write(self, reg_address, reg_value):
        cmd_w = self.reg_w_cmd + " " + reg_address + " " + reg_value
        # print(cmd_w)
        com_return = self.sendcmd(cmd_w)
        if com_return.split("\n")[0].strip() == cmd_w:
            return True
        else:
            wlogerror("ERROR:"+cmd_w)
            return False

    def reg_read(self, reg_address):
        cmd_r = self.reg_r_cmd + " " + reg_address
        com_return = self.sendcmd(cmd_r)
        if com_return.split("\n")[0].strip() == cmd_r:
            return com_return.split("\n")[1].strip().split("=")[1].strip()
        else:
            wlogerror("ERROR: "+cmd_r)
            return None

    def reg_write_bits(self, reg_address, bits_position, bits_value):
        """
        :param reg_address: 4034206c   # hex number
        :param bits_position:  num2:num1,   example: 2:0
        :param bits_value: 8 # dec number
        :return:
        """
        regvalue = self.reg_read(reg_address)
        new_regvalue = RegValue(regvalue).bits_modify(bits_position, bits_value)
        return self.reg_write(reg_address, new_regvalue)


if __name__ == "__main__":
    UART1 = Uart(3)
    UART1.open()
    for i in range(10):
        UART1.reg_write("40340010", "09000000")
        UART1.reg_write("4034202c", "10000")
        UART1.reg_write("4034206c", "10801ff")
        UART1.reg_write("40342030", "2041b7e7")
        UART1.reg_write("40344058", "05640000")
        UART1.reg_write("40344058", "05740000")
        UART1.reg_write("40344058", "057c0000")
        UART1.reg_write("4034402c", "0a001884")
        UART1.reg_write("40344030", "180BDA06")
        # aaa = UART1.reg_write("4034206c", "10800001")
        # print(aaa)
        # bbb = UART1.reg_read("4034206c")
        # print(bbb)
    UART1.close()
