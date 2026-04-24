from pyintf.gpib import *
from pyintf.uart import *
import re

REG_HIGH = "4034807c"  # bits[63:32]
REG_LOW = "40348078"


def SwMode(UART2):
    UART2.sendcmd("w 403440bc	0000000e")
    time.sleep(0.01)
    UART2.sendcmd("w 403440ac	000002aa")
    UART2.sendcmd("w 403440ac	00000000")
    UART2.sendcmd("w 403440bc	00000009")
    UART2.sendcmd("w 403440ac	00000444")
    UART2.sendcmd("w 403440ac	00000555")

def HwMode(UART2):
    UART2.sendcmd("w 403440ac	000005dd")
    UART2.sendcmd("w 403440ac	00000199")
    UART2.sendcmd("w 403440ac	00000088")
    UART2.sendcmd("w 403440ac	000002aa")
    UART2.sendcmd("w 403440ac	000003bb")
    UART2.sendcmd("w 403440bc	0000000e")
    UART2.sendcmd("w 403440bc	00000006")
    UART2.sendcmd("w 403440ac	000013bb")

def extract_hex_value(response):
    """从UART响应中提取16进制数值"""
    match = re.search(r"=\s*0x([0-9a-fA-F]+)", response)
    if not match:
        raise ValueError(f"无法解析寄存器值: {response}")
    return int(match.group(1), 16)

def get_bits(value, start, end):
    """从数值中提取指定位段（高位到低位）"""
    if start < end:
        raise ValueError("起始位必须大于结束位")
    mask = ((1 << (start - end + 1)) - 1) << end
    return (value & mask) >> end


def rapc(UART2,high_bit, low_bit):
    """
    读取指定位范围的值（从高位到低位）

    参数:
        high_bit: 最高位位置 (63-0)
        low_bit: 最低位位置 (必须 <= high_bit)

    返回:
        二进制字符串 (高位在前)
    """
    if not (0 <= low_bit <= high_bit <= 63):
        raise ValueError("位范围必须在0-63之间且high_bit >= low_bit")

    # 判断是否需要读取两个寄存器
    need_high = high_bit >= 32
    need_low = low_bit < 32

    # 读取寄存器值
    val_high, val_low = 0, 0
    if need_high:
        # resp = self.uart.sendcmd(f"r {self.REG_HIGH}")
        resp = UART2.sendcmd("r 4034807c")
        val_high = extract_hex_value(resp)
    if need_low:
        resp = UART2.sendcmd("r 40348078")
        val_low = extract_hex_value(resp)

    # 计算各寄存器中的位范围
    result_bits = []
    if need_high:
        reg_high_start = min(high_bit, 63) - 32
        reg_high_end = max(low_bit, 32) - 32
        bits = get_bits(val_high, reg_high_start, reg_high_end)
        result_bits.append(f"{bits:0{reg_high_start - reg_high_end + 1}b}")

    if need_low:
        reg_low_start = min(high_bit, 31)
        reg_low_end = low_bit
        bits = get_bits(val_low, reg_low_start, reg_low_end)
        result_bits.append(f"{bits:0{reg_low_start - reg_low_end + 1}b}")

    return "".join(result_bits)




def process_register(reg_val, start, end, value ,high_value_shift):
    """处理单个寄存器的位写入
    :param reg_val: 寄存器当前值
    :param high_bit: 要修改的最高位(全局位号)
    :param low_bit: 要修改的最低位(全局位号)
    :param value: 要写入的值(整数)
    :param reg_high: 该寄存器的最高位(全局位号)
    :param reg_low: 该寄存器的最低位(全局位号)
    :high_value_shift : 高位寄存器对
    :return: 修改后的寄存器值
    """
    # 计算该寄存器中需要修改的位范围
    # start_in_reg = high_bit - reg_low
    # end_in_reg = max(low_bit - reg_low,0)

    # 确保位范围在该寄存器内
    # if start_in_reg < 0 or end_in_reg > (reg_high - reg_low):
    #     return reg_val

    if start < end:
        raise ValueError("起始位必须大于结束位")

    bit_width = start - end + 1

    # 计算掩码和值部分
    mask = ((1 << bit_width) - 1) << end

    value_mask = (((1 << bit_width) - 1) << high_value_shift)
    value_part = ((value & value_mask) >> high_value_shift) << end

    return (reg_val & ~mask) | value_part


def read_reg(adress):
    resp = UART2.sendcmd(f"r {adress}")
    val_reg = extract_hex_value(resp)
    return val_reg



def wapc(UART2,high_bit, low_bit, binary_value):
    """
    跨寄存器位写入函数
    :param high_bit: 最高位(63-0)
    :param low_bit: 最低位(<=high_bit)
    :param binary_value: 要写入的数值可以是：
            - "1101" (二进制字符串)
            - 0b1101 (二进制字面量)
            - 13 (十进制整数)
    """
    # 参数校验
    if not (0 <= low_bit <= high_bit <= 63):
        raise ValueError("位范围必须在0-63之间且 high_bit >= low_bit")

    # 统一转换为整数
    if isinstance(binary_value, str):
        if not all(c in '01' for c in binary_value):
            raise ValueError("二进制字符串只能包含0和1")
        value = int(binary_value, 2)
    elif isinstance(binary_value, int):
        value = binary_value
    else:
        raise TypeError("输入必须是二进制字符串或整数")

    # if not all(c in '01' for c in str(bin(binary_value)).replace('0b', '')):
    #     raise ValueError("binary_value must contain only 0 and 1")

    need_high = high_bit >= 32
    need_low = low_bit < 32
    # 1. 读取当前寄存器值
    # val_high = extract_hex_value(UART2.sendcmd("r 4034807c")) if need_high else 0
    # val_low = extract_hex_value(UART2.sendcmd("r 40348078")) if need_low < 32 else 0

    # val_high = int('47cfc7ff', 16)
    # val_low = int('48d729e7', 16)

    val_high = read_reg(REG_HIGH)
    val_low = read_reg(REG_LOW)


    # total_bits = high_bit - low_bit + 1
    # if len(binary_value) > total_bits:
    #     raise ValueError("binary_value error")
    #     # value = value >> (len(binary_value) - total_bits)  # 截断高位

    if need_high & need_low:
        high_value_shift = 32-low_bit
    if need_high:
        reg_high_start = min(high_bit, 63) - 32
        reg_high_end = max(low_bit, 32) - 32
        val_high = process_register(val_high, reg_high_start, reg_high_end, value, high_value_shift)
        print(f'high {hex(val_high)}')
        ## write_reg(self.REG_HIGH, val_high)
        UART2.sendcmd(f"w {REG_HIGH}\t{val_high:08x}")

        # 处理低位寄存器 (bits[31:0])
    if need_low:
        reg_low_start = min(high_bit, 31)
        reg_low_end = low_bit
        val_low = process_register(val_low, reg_low_start, reg_low_end, value, 0)
        print(f'low {hex(val_low)}')
        UART2.sendcmd(f"w {REG_LOW}\t{val_low:08x}")



        # 4. 写回寄存器
    # if need_high:
    #     # write_reg(self.REG_HIGH, val_high)
    #     print(f'high {hex(val_high)}')
    # if need_low:
    #     # self._write_reg(self.REG_LOW, val_low)
    #     print(f'low {hex(val_low)}')



if __name__ == "__main__":

    UART2 = Uart(4, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    SwMode(UART2)
    ## val=UART2.sendcmd("r 403440ac")
    value=rapc(UART2,35,28)
    # print(value)
    # value=wapc(UART2,33,30,1000)
    wapc(UART2,35,29,0b1010101)
    HwMode(UART2)
    UART2.close()


