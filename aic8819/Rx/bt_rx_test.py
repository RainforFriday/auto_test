from icbasic.aicinstr.rs.cmp180 import *
from icbasic.aicintf import uart
import time


if __name__ == "__main__":
    host = "10.21.12.196"
    port = 5025
    BT = CMP180()
    BT.open_tcp(host, port)

    BT.sge_set_output_port("RF1.8")
    BT.set_repetition('Single')
    BT.set_count(1000)
    BT.set_start_mode()
    BT.set_sequencer_Freq(0, 2440)
    BT.set_sequencer_Level(0, -60)

    UART = uart.Uart(4)
    UART.open()

    desire_count = 50

    # flag = True
    count = 0
    while count != desire_count:
        UART.sendcmd("setrxstart")
        time.sleep(1)
        BT.sge_state('on')
        time.sleep(3)
        UART.sendcmd("setrxstop")
        time.sleep(1)
        BT.sge_state('off')
        time.sleep(0.5)
        print(UART.sendcmd("getrxresult"))
        time.sleep(0.5)

        count += 1
