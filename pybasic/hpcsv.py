# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@aicsemi.com 
@site:    
@software: PyCharm
@file: csv.py
@time: 2019/8/8 13:27
"""

import os
import sys
import csv
from pybasic.hplog import *


class HpCsv:
    def __init__(self):
        pass

    def read(self):
        pass

    def write(self, content, csv_file):
        """
        :param content: [["a","b","c"],["1","2","3"],["x","y","z"]]
        :param csv_file: "D:\test1\test2\test.csv"
        :return:
        """
        with open(csv_file, "w", newline="") as CSV_FILE:
            csv_write = csv.writer(CSV_FILE)
            for row in content:
                csv_write.writerow(row)


if __name__ == "__main__":
    print("this is a test print!!!")
