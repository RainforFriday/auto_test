# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: connection.py
@time: 2020/6/30 19:18
"""

import os
import sys
from enum import Enum


# Enums
class ConnectionMethod(Enum):
    tcpip = 'TCPIP'
    gpib = 'GPIB'
    usb = 'USB'

    def __str__(self):
        return self.value
