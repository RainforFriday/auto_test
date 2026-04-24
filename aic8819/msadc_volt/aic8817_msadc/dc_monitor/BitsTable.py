import os
import sys


class BitsTable:
    def __init__(self, table_path):
        self.table_path = table_path

    def read_table(self):
        items = []
        with open(self.table_path) as Table_FILE:
            for net_line in Table_FILE.readlines()[1:]:
                if net_line.strip().startswith(","):
                    pass
                else:
                    items.append(net_line)
        return items

    def bits_dict(self):
        d_bits = {}
        for bit_line in self.read_table():
            db_bit = BitsReg(bit_line)
            d_bits[db_bit.name] = db_bit
        return d_bits


class BitsReg:
    def __init__(self, bit_line):
        self.bit_info = bit_line

    @property
    def reg_name(self):
        return self.bit_info.split(",")[0].strip()

    @property
    def name(self):
        return self.bit_info.split(",")[1].strip()

    @property
    def address(self):
        return self.bit_info.split(",")[2].strip()

    @property
    def def_value(self):
        return self.bit_info.split(",")[3].strip()

    @property
    def pos(self):
        pos_end = self.bit_info.split(",")[7].strip()
        pos_start = self.bit_info.split(",")[8].strip()
        if pos_end == pos_start:
            return pos_end
        else:
            return pos_end+":"+pos_start

    @property
    def access(self):
        return self.bit_info.split(",")[9].strip()


if __name__ == "__main__":
    bit_table = "./aic8817/aic8822_bits_table.csv"
    aic8822_table = BitsTable(bit_table)
    print(aic8822_table.bits_dict()["rf_blk_remap_en0"].name)