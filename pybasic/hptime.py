# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@aicsemi.com 
@site:    
@software: PyCharm
@file: timelib.py
@time: 2019/8/8 19:54
"""

import os
import sys
import time


class HpTime:
    def __init__(self):
        self.ticks = time.time()

    def date_time(self):
        return time.strftime("%Y%m%d_%H%M%S", time.localtime())


if __name__ == "__main__":
    pass
