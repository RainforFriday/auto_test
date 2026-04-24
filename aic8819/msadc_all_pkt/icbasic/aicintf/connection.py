# encoding: utf-8
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
