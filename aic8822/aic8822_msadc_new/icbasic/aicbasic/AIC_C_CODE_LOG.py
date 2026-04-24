import os
import sys
from aicbasic.aiclog import *
import time


def AIC_C_CODE_LOG(EN=False, LOGFILENAME = "./aiclog/aiclog"):
    if EN:
        global logfile
        global logf
        logf_create(LOGFILENAME, Formatter=False)
        wlog("START @ " + time.asctime( time.localtime(time.time()) ))
    else:
        pass
    global CCODE
    CCODE = EN


if __name__ == "__main__":
    AIC_C_CODE_LOG()
