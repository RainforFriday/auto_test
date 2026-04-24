from pyintf.uart import *
from aic8819.aic8819_tunnertest.aic8819_tunner_txtest.apc8819 import *
import random
import csv
import datetime



def meas_fsq():
    # 假设的测量函数，返回一个模拟的功率值
    return round(random.uniform(5, 10), 3)# 返回一个模拟的功率值

def PwrRegulate(UART2, start, end, value):
    # 计算len
    length = start - end + 1
    pwrs = []
    head = []

    # 执行循环
    for i in range(2 ** length):
        head.append('pwr' + str(i))
        # wapc(UART2, start, end, i)  # 执行wapc操作
        # time.sleep(0.5)
        pwr = meas_fsq()  # 获取功率值
        pwrs.append(pwr)  # 保存功率值

    # 再次执行wapc和测量
    # wapc(UART2, start, end, value)
    pwr = meas_fsq()
    pwrs.append(pwr)

    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    current_time = '1'
    file = r'aic8819_PwrRegulate_' + current_time + ".csv"
    # 写入CSV文件
    with open(file, mode='a+', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['bits', 'init_value'] + head + ['init_pwr'])

        # 写入第二行：{start}:{end}, pwrs 和 3 个换行符
        formatted_string = f"{start}~{end}"
        writer.writerow([f'{formatted_string}'] + [value] + pwrs )
        # 添加空三行
        for _ in range(3):
            writer.writerow([])  # 写入空行

    print(f"Data written for {start}:{end} : {pwrs}")

# 示例调用
# PwrRegulate("UART2", 1, 3, 0b1110001)



if __name__ == "__main__":

    UART2 = Uart(4, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # SwMode(UART2)


    start, end = 2, 0

    # value=rapc(UART2,2,0)
    value = '1'
    value = int(value, 2)
    # wapc(UART2, start, end, value)
    PwrRegulate(UART2,start,end,value)

    start, end = 6, 3
    value = int(rapc(UART2,start,end), 2)
    PwrRegulate(UART2,start,end,value)

    start, end = 11, 7
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 17, 12
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 23, 18
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 28, 27
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 31, 29
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 36, 32
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 42, 37
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 51, 47
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 54, 52
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 57, 55
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 58, 58
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)

    start, end = 63, 59
    value = int(rapc(UART2, start, end), 2)
    PwrRegulate(UART2, start, end, value)








