# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: cmdlib.py
@time: 2019/8/31 16:46
"""

import os
import sys
import subprocess
from pybasic.hpdecor import *
from pybasic.hplog import *


class Cmd3(object):
    """
    for python3
    """
    def __init__(self, cmd_line=""):
        self.cmd = cmd_line

    @decor_catch_exception
    def run(self):
        # return STATUS OUTPUT
        # command succeed----> STATUS: True , Failed: False
        # OUTPUT STDOUT
        (flag, output) = subprocess.getstatusoutput(self.cmd)
        # print(type(flag))
        if flag == 0:
            status = True
        else:
            status = False
        return [status, output]


class Cmd2(object):
    """
    for python2
    """
    def __init__(self, cmd_line=""):
        self.cmd = cmd_line

    @decor_check_action
    def run(self):
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
        return "".join(p.stdout.readlines())


class Cmd(Cmd2):
    def __init__(self, cmd_line=""):
        super(Cmd, self).__init__(cmd_line)


if __name__ == "__main__":
    command = "ls -la"
    aaa = Cmd2(command)
    aaa.run()
    print(aaa)
