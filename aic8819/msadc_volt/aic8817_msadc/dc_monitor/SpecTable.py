import os
import sys
from icbasic.aicbasic.aicnum import *


class bit_table:
    def __init__(self, table_path):
        self.reg_table_path = table_path

    def load(self):
        with open(self.reg_table_path, "r") as REG_TABLE:
            pass


class SpecTable:
    def __init__(self, spec_path):
        self.spec_path = spec_path

    def read_table(self):
        items = []
        #print(self.spec_path)
        with open(self.spec_path) as SPEC_FILE:
            for net_line in SPEC_FILE.readlines()[2:]:
                if net_line.strip().startswith(","):
                    pass
                else:
                    items.append(net_line)
        return items

    def db_nets(self):
        l_db_nets = []
        for net_line in self.read_table():
            l_db_nets.append(DCNet(net_line))
        return l_db_nets

    def db_nets_by_band(self, band_sel):
        # l_band_sel = ["WF_LB", "WF_HB", "WF_6E", "WF"]
        # band_sel = "WF_HB"
        l_db_nets = []
        if type(band_sel) is str:
            l_band_sel = [band_sel]
        else:
            l_band_sel = band_sel
        for net_line in self.read_table():
            print(self.read_table())
            print(net_line)
            db_net = DCNet(net_line)
            if db_net.test_band in l_band_sel:
                l_db_nets.append(db_net)
        return l_db_nets

    def db_nets_by_block(self, block_sel):
        # block_sel = ["pa_hb0", "pa_lb0"]
        # block_sel = "pa_hb0"
        # block_sel = "all"
        l_db_nets = []
        if block_sel=="all":
            for net_line in self.read_table():
                db_net = DCNet(net_line)
                l_db_nets.append(db_net)
        else:

            if type(block_sel) is str:
                l_block_sel = [block_sel]
            else:
                l_block_sel = block_sel
            for net_line in self.read_table():
                db_net = DCNet(net_line)
                #print(self.read_table())
                #print(net_line)
                #print([db_net.block])
                #print(l_block_sel)
                if db_net.block.rsplit("_") [0] in l_block_sel:
                    #print(1)
                    l_db_nets.append(db_net)
                    #print(l_db_nets)
        #print(l_db_nets)
        if l_db_nets==[]:
            print(block_sel+" not found in apc")
        else:
            return l_db_nets


class DCNet:
    def __init__(self, net_info_line):
        self.info_line = net_info_line
        self.info_list = self.info_line.strip().split(",")

    @staticmethod
    def change_bindata_style(bin_data):
        # bin_data = 1'b1
        # return 0b1
        if "b" in bin_data:
            return "0b" + bin_data.split("b")[-1]
        else:
            return bin_data

    @property
    def name(self):
        return self.sub_top + "_" + self.block + "_" + self.net_name

    @property
    def net_name(self):
        return self.info_list[0].strip()

    @property
    def sub_top(self):
        return self.info_list[1].strip()

    @property
    def block(self):
        return self.info_list[2].strip()

    @property
    def enable_reg_name(self):
        return self.info_list[5].strip()

    @property
    def enable_reg_value(self):
        # return aicNum(self.info_list[6].strip()).DEC
        return aicNum(self.change_bindata_style(self.info_list[6].strip())).DEC

    @property
    def mode_reg_name(self):
        return self.info_list[7].strip()

    @property
    def mode_reg_value(self):
        return aicNum(self.change_bindata_style(self.info_list[8].strip())).DEC

    @property
    def bits_reg_name(self):
        return self.info_list[9].strip()

    @property
    def bits_reg_value(self):
        return aicNum(self.change_bindata_style(self.info_list[10].strip())).DEC

    @property
    def test_case(self):
        return self.info_list[11].strip()

    @property
    def test_band(self):
        return self.info_list[12].strip()


if __name__ == "__main__":
    spec_path_aic = "./aic8817/aic8817_spec_testability_1.csv"
    spec_path = "./aic8817/aic8822_spec_testability_20240606.csv"
    spec_aic8822 = SpecTable(spec_path_aic)
    xxx = spec_aic8822.read_table()
    for dc_net in spec_aic8822.db_nets():
        print(dc_net.name)
        print(dc_net.test_case)
        print(dc_net.test_band)
        print(dc_net.bits_reg_value)
        print(dc_net.mode_reg_value)
        print(dc_net.enable_reg_value)
        #print(netx.enable_reg_address)
        #print(netx.enable_reg_pos)
        #print(netx.mode_reg_address)
        #print(netx.mode_reg_pos)
        #print(netx.bits_reg_address)
        #print(netx.bits_reg_pos)
        print("\n")