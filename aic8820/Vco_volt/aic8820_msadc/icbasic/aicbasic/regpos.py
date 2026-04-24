import os
import sys
from aicbasic.aicnum import *

# this function


class REG_POS_VALUE:
    def __init__(self, reg_pos_list, reg_value_list):
        self.reg_pos_list = reg_pos_list
        self.reg_value_list = reg_value_list
        if len(reg_pos_list) != len(reg_value_list):
            print("ERROR : length of reg pos and value not the same!!! ")
            sys.exit(0)

    def pos_c_code(self):
        pos_c_list = []
        for pos in self.reg_pos_list:
            if ":" in pos:
                pos_start = int(pos.split(":")[0])
                pos_stop = int(pos.split(":")[1])
                if pos_start < pos_stop:
                    print("START POS SHOULD BE BIGGER THEN STOP POS")
                    sys.exit()
                pos_len = abs(pos_start - pos_stop) + 1
                pos_mask_value = pow(2 , pos_len) - 1
                pos_c_str = "(" + aicNum().dec2hex(pos_mask_value) + "<<" + str(pos_stop) + ")"
            else:
                pos_c_str = "(" + aicNum().dec2hex(1) + "<<" + str(pos) + ")"
            pos_c_list.append(pos_c_str)
        if len(pos_c_list) == 1:
            return pos_c_list[0]
        else:
            return "(" + "|".join(pos_c_list) + ")"

    def value_c_code(self):
        value_c_list = []
        for num_index in range(len(self.reg_pos_list)):
            pos = self.reg_pos_list[num_index]
            if ":" in pos:
                pos_start = int(pos.split(":")[0])
                pos_stop = int(pos.split(":")[1])
                if pos_start < pos_stop:
                    print("START POS SHOULD BE BIGGER THEN STOP POS")
                    sys.exit()
                pos_len = abs(pos_start - pos_stop) + 1
            else:
                pos_stop = int(pos)
                pos_len = 1

            pos_value = self.reg_value_list[num_index]
            value_c_str = "(" + aicNum().dec2hex(pos_value) + "<<" + str(pos_stop) + ")"
            value_c_list.append(value_c_str)
        if len(value_c_list) == 1:
            return value_c_list[0]
        else:
            return "(" + "|".join(value_c_list) + ")"

    def c_code(self):
        return self.value_c_code() + "," + self.pos_c_code()


if __name__ == "__main__":
    reg_pos_list = ["31:30", "2", "1:0"]
    reg_value_list = [2,1,0]
    reg_posx = REG_POS_VALUE(reg_pos_list, reg_value_list)
    aaa = reg_posx.pos_c_code()
    bbb = reg_posx.value_c_code()
    print(aaa)
    print(bbb)
