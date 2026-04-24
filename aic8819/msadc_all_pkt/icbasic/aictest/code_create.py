import os
import sys
from aicintf.uart import *
from aicbasic.AIC_C_CODE_LOG import *


if __name__ == "__main__":
    AIC_C_CODE_LOG(EN=True)
    UART1 = Uart()
    UART1.write_reg_mask("40344000", ["12:11","8","1:0"], [1,0,3])
    closelog()