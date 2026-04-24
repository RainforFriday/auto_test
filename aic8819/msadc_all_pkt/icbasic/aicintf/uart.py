# encoding: utf-8

import os
import sys
from aicintf.com import *
from aicbasic.regvalue import *
from aicbasic.regpos import *
from aicbasic.aiclog import *


class Uart(COM):
    def __init__(self, com_port=3, wr_mode=True):
        super(Uart, self).__init__(com_port)
        if wr_mode:
            self.reg_w_cmd = "w"
            self.reg_r_cmd = "r"
        else:
            self.reg_w_cmd = "mw"
            self.reg_r_cmd = "md"

    def write_reg(self, reg_address, reg_value):
        cmd_w = self.reg_w_cmd + " " + reg_address + " " + aicNum(reg_value).HEX
        #print(cmd_w)
        com_return = self.sendcmd(cmd_w)
        if com_return.split("\n")[0].strip() == cmd_w:
            return True
        else:
            wlogerror("ERROR:"+cmd_w)
            return False

    def read_reg(self, reg_address):
        try:
            cmd_r = self.reg_r_cmd + " " + reg_address
            com_return = self.sendcmd(cmd_r)
            # print("@@@")
            # print(com_return)
            """ del check cmd
            if com_return.split("\n")[0].strip() == cmd_r:
                return com_return.split("\n")[1].strip().split("=")[1].strip()
            else:
                wlogerror("ERROR: "+cmd_r)
                return None
            """
            if True:
                return com_return.split("\n")[1].strip().split("=")[1].strip()

        except Exception as e:
            wlogerror(e)

    def read_reg_bits(self, reg_address, reg_pos):
        """
        :param reg_address:  hex "0x40344000"
        :param reg_pos:   str: "13:10"
        :return:
        """
        ## return dec value
        reg_value_hex = self.read_reg(reg_address)
        reg_value_dec = int(aicNum(reg_value_hex).DEC)
        if ":" not in reg_pos:
            reg_pos_start = int(reg_pos)
            reg_pos_stop = int(reg_pos)
        else:
            reg_pos_start = int(reg_pos.split(":")[0])
            reg_pos_stop = int(reg_pos.split(":")[1])
        reg_pos_width = abs(reg_pos_start - reg_pos_stop) + 1
        reg_pos_mask = (pow(2, reg_pos_width) - 1) << min(reg_pos_start, reg_pos_stop)
        return ((reg_value_dec & reg_pos_mask) >> min(reg_pos_start, reg_pos_stop))

    def write_reg_bits(self, reg_address, bits_position, bits_value):
        """
        :param reg_address: 4034206c   # hex number
        :param bits_position:  num2:num1,   example: 2:0
        :param bits_value: 8 # dec number/hex/oct.
        hex: "0xf"
        dec: "0d9", "9"
        oct: "0o4"
        bin: "0b110"
        :return:
        """
        bits_value_dec = aicNum(str(bits_value)).DEC
        # print("$$$")
        # print(reg_address)
        reg_value_hex = self.read_reg(reg_address)
        return self.write_reg(reg_address, self.__reg_value_modify_bits__(reg_value_hex, bits_position, bits_value_dec))

    def write_reg_mask(self, address, bits_pos, bits_value, comment=""):
        """
        Args:
            address: 40344000
            bits_list: ["30:28","16:13","1:0"]
            value_list: [3,8,2]
        Returns:
            Ture/False
        """
        if type(bits_pos) is not list:
            bits_pos_list = [bits_pos]
        else:
            bits_pos_list = bits_pos

        if type(bits_value) is not list:
            bits_value_list = [bits_value]
        else:
            bits_value_list = bits_value

        if True:
            if len(bits_pos_list) != len(bits_value_list):
                wlogerror("Length of BitPos and BitValue Not the same!")
                sys.exit(0)
            else:
                for pos_index in range(len(bits_pos_list)):
                    self.write_reg_bits(address, bits_pos_list[pos_index], bits_value_list[pos_index])
            ## create c code
            c_code = "write_reg_mask(" + address + "," + REG_POS_VALUE(bits_pos_list, bits_value_list).c_code() + ")"
            # wlog(c_code)

    def __reg_value_modify_bits__(self, old_reg_value_hex, reg_bits_pos, reg_bits_value_dec):
        if ":" not in reg_bits_pos:
            reg_pos_start = int(reg_bits_pos)
            reg_pos_stop = int(reg_bits_pos)
        else:
            reg_pos_start = int(reg_bits_pos.split(":")[0])
            reg_pos_stop = int(reg_bits_pos.split(":")[1])
        reg_pos_width = abs(reg_pos_start - reg_pos_stop) + 1
        reg_address_mask = ~((pow(2, reg_pos_width) - 1) << min(reg_pos_start, reg_pos_stop))
        reg_value_mask = aicNum(reg_bits_value_dec).DEC << min(reg_pos_start, reg_pos_stop)
        # print("###")
        # print(old_reg_value_hex)
        new_reg_value = aicNum(aicNum(old_reg_value_hex).DEC & reg_address_mask | reg_value_mask).HEX
        return new_reg_value


if __name__ == "__main__":
    UART1 = Uart(12)
    UART1.open()
    aaa = UART1.read_reg("40344054")
    #UART1.write_reg_bits("40344028", "3:0", 6)
    bbb = UART1.read_reg_bits("40344054", "22:19")
    #ccc = UART1.read_reg_bits("40344028", "3:0")
    #aaa = UART1.__reg_value_modify_bits__("0xffffffff", "7:4", 5)
    print(aaa)
    print(bbb)
    #print(ccc)
    #UART1.open()
    #UART1.write_reg_mask("40344000", ["32:12","9", "1:0"], [12,1,3])
    """
    for i in range(10):
        UART1.write_reg_mask("40340010", "09000000")
        UART1.write_reg_mask("4034202c", "10000")
        UART1.write_reg_mask("4034206c", "10801ff")
        UART1.write_reg_mask("40342030", "2041b7e7")
        UART1.write_reg_mask("40344058", "05640000")
        UART1.write_reg_mask("40344058", "05740000")
        UART1.write_reg_mask("40344058", "057c0000")
        UART1.write_reg_mask("4034402c", "0a001884")
        UART1.write_reg_mask("40344030", "180BDA06")
        # aaa = UART1.reg_write("4034206c", "10800001")
        # print(aaa)
        # bbb = UART1.reg_read("4034206c")
        # print(bbb)
    """
    UART1.close()