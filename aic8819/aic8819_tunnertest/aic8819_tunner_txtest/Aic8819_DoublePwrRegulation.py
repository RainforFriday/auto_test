from pyintf.uart import *
from aic8819.aic8819_tunnertest.aic8819_tunner_txtest.apc8819 import *
import random
import csv
import datetime



def meas_fsq():
    # 假设的测量函数，返回一个模拟的功率值
    return round(random.uniform(5, 10), 3)# 返回一个模拟的功率值

def DoublePwrRegulate(UART2, start1, end1, value1, start2, end2, value2):
    length1 = start1 - end1 + 1
    length2 = start2 - end2 + 1

    # 初始化功率矩阵
    pwrs_matrix = []

    # current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")
    current_time = '1'
    file = r'aic8819_Double_PwrRegulate_' + current_time + ".csv"
    # 写入CSV文件
    with open(file, mode='a+', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header0 = ['bits_1'] + [f'{start1}~{end1}'] + ['init_value1'] + [value1] + ['\n', '\n'] + \
                  ['bits_2'] + [f'{start2}~{end2}'] + ['init_value2'] + [value2]

        writer.writerow(header0)
        # 第一行，列名：空格，pwr0, pwr1, ..., pwr{length2}
        header1 = ['Out\Inner'] + [f"pwr{j}" for j in range(2 ** length2)]
        writer.writerow(header1)

        # 外循环，长度为 length1
        for i in range(2 ** length1):
            # 生成外循环的行名（例如：pwr0, pwr1, ..., pwr{length1})
            row_name = f"pwr{i}"
            row_data = [row_name]  # 第一列放行名
            # wapc(UART2, start1, end1, i)  # 执行wapc操作
            # time.sleep(0.5)
            # pwr = meas_fsq()  # 获取功率值

            # 内循环，长度为 length2
            for j in range(2 ** length2):
                # 执行wapc和测量功率
                # wapc(UART2, start2, end2, j)
                # time.sleep(0.5)
                pwr = meas_fsq()  # 获取功率值
                row_data.append(pwr)  # 添加功率值到当前行数据

            # 写入当前行数据
            writer.writerow(row_data)

    print("数据已成功写入到 output.csv")


    # 再次执行wapc和测量
    # wapc(UART2, start1, end1, value1)
    # time.sleep(0.5)
    # wapc(UART2, start2, end2, value2)
    # pwr = meas_fsq()
    # pwrs.append(pwr)



if __name__ == "__main__":

    UART2 = Uart(4, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    # SwMode(UART2)

    start1, end1 = 6, 3
    start2, end2 = 2, 0

    # value=rapc(UART2,2,0)

    value1 = int('1', 2)
    value2 = int('1', 2)
    # wapc(UART2, start, end, value)

    DoublePwrRegulate(UART2,start1,end1,value1,start2,end2,value2)


    # PwrRegulate(UART2,start,end,value)








