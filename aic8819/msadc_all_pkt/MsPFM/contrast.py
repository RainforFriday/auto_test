
a = 168732132
# b = 425984
b = 169255472


# 转换为二进制字符串（方便查看）
print("a =", bin(a))
print("b =", bin(b))

# 找出需要比较的最大位数（取两者二进制长度的较大值）
max_bits = max(a.bit_length(), b.bit_length())

# 逐位比较
for i in range(max_bits):
    bit_a = (a >> i) & 1  # 提取第 i 位 (最低位 i=0)
    bit_b = (b >> i) & 1
    if bit_a != bit_b:
        print(f"位 {i}: a={bit_a}, b={bit_b}")






class MSADC:
    def __init__(self, clk_div=40, acc_mode=1):
        self.Mult = 1.0
        self.ClkDiv = clk_div
        if acc_mode == 0:
            self.Window = 256
            self.Denom = 8256
        elif acc_mode == 1:
            self.Window = 512
            self.Denom = 32896
        elif acc_mode == 2:
            self.Window = 1024
            self.Denom = 131328
        elif acc_mode == 3:
            self.Window = 4032
            self.Denom = 2033136
        else:
            raise "'acc_mode' is out of range"
        self.clkdivAddr = "40100038"
        self.vddSenAddr = "70001004"
        self.msAddr = "4010d004"
        self.winAddr = "4010d008"
        self.anaAddr = "4010d00c"
        self.roAddr = "4010d010"



UARTc.write_reg_mask(self.clkdivAddr, ["8", "7:0"], [1, 40])
UARTc.write_reg_mask(self.winAddr, "27:16", 512)
UARTc.write_reg_mask(self.anaAddr, ["28:27", "26:25", "24:21", "18:15",   "14:12", "1"],
                                   [ 1,       1,       0,  int('1101', 2), 2,       0])

UARTc.write_reg_mask(self.anaAddr, ["20", "19", "10", "9:2"], [0, 1, 1, int('79', 16)],
                             "ts_mode/adc_ff_en/sdm_mode/others")

UARTc.write_reg_mask(self.winAddr, "3:0", 0)
UARTc.write_reg_mask(self.winAddr, "28", 1)
UARTc.write_reg_mask(self.anaAddr, ["11", "0"], [0, 0])

