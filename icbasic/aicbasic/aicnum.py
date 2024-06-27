# encoding: utf-8
import os
import sys
from aicbasic.aiclog import *

degree_sign = u"\N{DEGREE SIGN}"


def signed2dec(din, width):
    if din > pow(2, width-1):
        dout = din - pow(2, width)
    else:
        dout = din
    return dout


def dec2signed(din, width):
    if din < 0:
        dout = din + pow(2, width)
    else:
        dout = din
    return dout


class aicNum:
    def __init__(self, num=None):
        # global definition
        # base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F]
        # self.base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]
        self.num = num
        self.system = self.system_check()

    def system_check(self):
        if str(self.num).strip().startswith("0X") or str(self.num).strip().startswith("0x"):
            return "HEX"
        elif str(self.num).strip().startswith("0O") or str(self.num).strip().startswith("0o"):
            return "OCT"
        elif str(self.num).strip().startswith("0B") or str(self.num).strip().startswith("0b"):
            return "BIN"
        elif str(self.num).strip().startswith("0D") or str(self.num).strip().startswith("0d"):
            return "DEC"
        elif str.isdecimal(str(self.num).strip()):
            return "DEC"
        else:
            return None

    @property
    def BIN(self):
        if self.system == "HEX":
            return self.hex2bin(self.num)
        elif self.system == "OCT":
            return self.oct2bin(self.num)
        elif self.system == "BIN":
            return self.num
        elif self.system == "DEC":
            return self.dec2bin(self.num)
        else:
            return None

    @property
    def DEC(self):
        if self.system == "HEX":
            return self.hex2dec(self.num)
        elif self.system == "OCT":
            return self.oct2dec(self.num)
        elif self.system == "BIN":
            return self.bin2dec(self.num)
        elif self.system == "DEC":
            return int(self.num)
        else:
            return None

    @property
    def HEX(self):
        if self.system == "HEX":
            return self.num
        elif self.system == "OCT":
            return self.oct2hex(self.num)
        elif self.system == "BIN":
            return self.bin2hex(self.num)
        elif self.system == "DEC":
            return self.dec2hex(self.num)
        else:
            return None

    @property
    def OCT(self):
        if self.system == "HEX":
            return self.hex2oct(self.num)
        elif self.system == "OCT":
            return self.num
        elif self.system == "BIN":
            return self.bin2oct(self.num)
        elif self.system == "DEC":
            return self.dec2oct(self.num)
        else:
            return None

    @staticmethod
    def bin2dec(num):
        return int(num, 2)

    @staticmethod
    def oct2dec(num):
        return int(num, 8)

    @staticmethod
    def hex2dec(num):
        return int(num, 16)

    @staticmethod
    def dec2bin(num):
        return bin(int(num))

    @staticmethod
    def hex2bin(num):
        return bin(int(num, 16))

    @staticmethod
    def oct2bin(num):
        return bin(int(num, 8))

    @staticmethod
    def dec2hex(num):
        return hex(int(num))

    @staticmethod
    def bin2hex(num):
        return hex(int(num, 2))

    @staticmethod
    def oct2hex(num):
        return hex(int(num, 8))

    @staticmethod
    def dec2oct(num):
        return oct(int(num))

    @staticmethod
    def bin2oct(num):
        return oct(int(num, 2))

    @staticmethod
    def hex2oct(num):
        return oct(int(num, 16))


if __name__ == "__main__":
    number_in = 12
    data = aicNum(number_in)
    print(data.BIN)
