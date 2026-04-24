# from pyintf.gpib import *
# from pyintf.uart import *
import re
import time

# REG_HIGH = "4034807c"  # bits[63:32]
# REG_LOW = "40348078"

# REG_LOW = "40348060"
# REG_HIGH = "40348064"  # bits[63:32]



class ApcReg():
    def __init__(self, UART2, REG_LOW = "40348060", REG_HIGH = "40348064", ):
        # super(self).__init__()
        self.UART2 = UART2
        self.REG_LOW = REG_LOW
        self.REG_HIGH = REG_HIGH

    # def global_create():
    #     global REG_LOW
    #     # REG_LOW = "40348060"
    #     global REG_HIGH  # bits[63:32]
    #     # REG_HIGH = "40348064"

    def swMode(self):
        self.UART2.sendcmd("w 403440bc	0000000e")
        time.sleep(0.01)
        self.UART2.sendcmd("w 403440ac	000002aa")
        self.UART2.sendcmd("w 403440ac	00000000")
        self.UART2.sendcmd("w 403440bc	00000009")
        self.UART2.sendcmd("w 403440ac	00000444")
        self.UART2.sendcmd("w 403440ac	00000555")

    def hwMode(self):
        self.UART2.sendcmd("w 403440ac	000005dd")
        self.UART2.sendcmd("w 403440ac	00000199")
        self.UART2.sendcmd("w 403440ac	00000088")
        self.UART2.sendcmd("w 403440ac	000002aa")
        self.UART2.sendcmd("w 403440ac	000003bb")
        self.UART2.sendcmd("w 403440bc	0000000e")
        self.UART2.sendcmd("w 403440bc	00000006")
        self.UART2.sendcmd("w 403440ac	000013bb")

    def print_red(self, text):
        print(f"\033[31m{text}\033[0m")

    def extract_hex_value(self,response):
        """从UART响应中提取16进制数值"""

        match = re.search(r"=\s*0x([0-9a-fA-F]+)", response)
        if not match:
            raise ValueError(f"无法解析寄存器值: {response}")
        return int(match.group(1), 16)

    def get_bits(self,value, start, end):
        """从数值中提取指定位段（高位到低位）"""
        if start < end:
            raise ValueError("起始位必须大于结束位")
        mask = ((1 << (start - end + 1)) - 1) << end
        return (value & mask) >> end

    def read_reg_pos(self, high_bit, low_bit):
        """
                读取指定位范围的值（从高位到低位）

                参数:
                    high_bit: 最高位位置 (31-0)
                    low_bit: 最低位位置 (必须 <= high_bit)

                返回:
                    二进制字符串 (高位在前)
                """
        if not (0 <= low_bit <= high_bit <= 31):
            raise ValueError("位范围必须在0-63之间且high_bit >= low_bit")

        time.sleep(0.8)
        resp = self.UART2.sendcmd(f"r {self.REG_LOW}")
        val_low = self.extract_hex_value(resp)

        # 计算各寄存器中的位范围
        result_bits = []
        reg_low_start = min(high_bit, 31)
        reg_low_end = low_bit
        bits = self.get_bits(val_low, reg_low_start, reg_low_end)
        result_bits.append(f"{bits:0{reg_low_start - reg_low_end + 1}b}")

        return "".join(result_bits)


    def write_reg_pos(self,high_bit, low_bit, binary_value):
        """
        跨寄存器位写入函数
        :param high_bit: 最高位(31-0)
        :param low_bit: 最低位(<=high_bit)
        :param binary_value: 要写入的数值可以是：
                - "1101" (二进制字符串)
                - 0b1101 (二进制字面量,不要1101)
                - 13 (十进制整数)
        """
        # 参数校验
        if not (0 <= low_bit <= high_bit <= 31):
            raise ValueError("位范围必须在0-31之间且 high_bit >= low_bit")

        # 统一转换为整数
        if isinstance(binary_value, str):
            if not all(c in '01' for c in binary_value):
                raise ValueError("二进制字符串只能包含0和1")
            value = int(binary_value, 2)
        elif isinstance(binary_value, int):
            value = binary_value
        else:
            raise TypeError("输入必须是二进制字符串或整数")

        val_low = self.read_reg(self.REG_LOW)

        reg_low_start = min(high_bit, 31)
        reg_low_end = low_bit
        val_low = self.process_register(val_low, reg_low_start, reg_low_end, value, 0)
        print(f'to be written: {hex(val_low)}')
        # self.swMode()
        self.UART2.sendcmd(f"w {self.REG_LOW}\t{val_low:08x}")
        # time.sleep(0.1)
        # val_read = self.read_reg_pos(high_bit, low_bit)
        # print("read: ", val_read)
        # verify_flag = self.verify_value(value,val_read,high_bit, low_bit)
        # if not verify_flag:
        #     self.print_red(f'Write failed!, Write {value} is not equal to read {val_read}')
        # else:
        #     print('Successfully written')


    def verify_value(self, value, target_str, high_bit, low_bit):
        reg_low_start = min(high_bit, 31)
        reg_low_end = low_bit
        # 将value转换为相同格式的二进制字符串
        value_bits = f"{value:0{reg_low_start - reg_low_end + 1}b}"

        # 比较两个二进制字符串
        return value_bits == target_str


    def rapc(self, high_bit, low_bit):
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
            self.swMode()
            resp = self.UART2.sendcmd(f"r {self.REG_HIGH}")
            self.hwMode()
            val_high = self.extract_hex_value(resp)
        if need_low:
            self.swMode()
            resp = self.UART2.sendcmd(f"r {self.REG_LOW}")
            self.hwMode()
            val_low = self.extract_hex_value(resp)

        # 计算各寄存器中的位范围
        result_bits = []
        if need_high:
            reg_high_start = min(high_bit, 63) - 32
            reg_high_end = max(low_bit, 32) - 32
            bits = self.get_bits(val_high, reg_high_start, reg_high_end)
            result_bits.append(f"{bits:0{reg_high_start - reg_high_end + 1}b}")

        if need_low:
            reg_low_start = min(high_bit, 31)
            reg_low_end = low_bit
            bits = self.get_bits(val_low, reg_low_start, reg_low_end)
            result_bits.append(f"{bits:0{reg_low_start - reg_low_end + 1}b}")

        return "".join(result_bits)




    def process_register(self, reg_val, start, end, value ,high_value_shift):
        """处理单个寄存器的位写入
        :param reg_val: 寄存器当前值
        :param high_bit: 要修改的最高位(全局位号)
        :param low_bit: 要修改的最低位(全局位号)
        :param value: 要写入的值(整数)
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


    def read_reg(self, adress):
        # self.swMode()
        time.sleep(0.6)
        resp = self.UART2.sendcmd(f"r {adress}")
        # self.hwMode()
        val_reg = self.extract_hex_value(resp)
        return val_reg



    def wapc(self,high_bit, low_bit, binary_value):
        """
        跨寄存器位写入函数，带swMode;
        :param high_bit: 最高位(63-0)
        :param low_bit: 最低位(<=high_bit)
        :param binary_value: 要写入的数值可以是：
                - "1101" (二进制字符串)
                - 0b1101 (二进制字面量,不要1101)
                - 0xc (16进制)
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


        # if need_high & need_low:
        #     high_value_shift = 32-low_bit
        if need_high:
            high_value_shift = max(0, 32 - low_bit)

            self.swMode()
            val_high = self.read_reg(self.REG_HIGH)
            self.hwMode()

            reg_high_start = min(high_bit, 63) - 32
            reg_high_end = max(low_bit, 32) - 32
            val_high = self.process_register(val_high, reg_high_start, reg_high_end, value, high_value_shift)
            # print(f'high {hex(val_high)}')
            ## write_reg(self.REG_HIGH, val_high)
            self.swMode()
            self.UART2.sendcmd(f"w {self.REG_HIGH}\t{val_high:08x}")
            self.hwMode()

            # 处理低位寄存器 (bits[31:0])
        if need_low:
            self.swMode()
            val_low = self.read_reg(self.REG_LOW)
            self.hwMode()

            reg_low_start = min(high_bit, 31)
            reg_low_end = low_bit
            val_low = self.process_register(val_low, reg_low_start, reg_low_end, value, 0)
            print(f'low {hex(val_low)}')
            self.swMode()
            self.UART2.sendcmd(f"w {self.REG_LOW}\t{val_low:08x}")
            self.hwMode()



            # 4. 写回寄存器
        # if need_high:
        #     # write_reg(self.REG_HIGH, val_high)
        #     print(f'high {hex(val_high)}')
        # if need_low:
        #     # self._write_reg(self.REG_LOW, val_low)
        #     print(f'low {hex(val_low)}')



    # def wf_tx_gain_reg(self):
    #     self.REG_LOW='403440a0'
    #     self.wapc(14,0,)


    def fix_apc_low_table_gain(self):
        self.REG_LOW = '403440a0'
        self.write_reg_pos(14, 14, 0b1)    # tx_gain_dr
        self.write_reg_pos(8, 0, 0b00001001)   # 0x09
        self.write_reg_pos(15, 15, 0b1)   # tx_gain_dr_pulse


    def fix_apc_high_table_gain(self):
        self.REG_LOW = '403440a0'
        self.write_reg_pos(14, 14, 0b1)    # tx_gain_dr
        self.write_reg_pos(8, 0, 0b10101100)   # 0xac
        self.write_reg_pos(15, 15, 0b1)   # tx_gain_dr_pulse


    def fix_apc_table_gain(self, val):
        self.REG_LOW = '403440a0'
        self.write_reg_pos(14, 14, 0b1)    # tx_gain_dr
        self.write_reg_pos(8, 0, val)   # 0xac
        self.write_reg_pos(15, 15, 0b1)   # tx_gain_dr_pulse

    def release_apc_high_table_gain(self):
        self.REG_LOW = '403440a0'
        self.write_reg_pos(15, 15, 0b0)   # tx_gain_dr_pulse
        self.write_reg_pos(14, 14, 0b0)     # tx_gain_dr
        # self.write_reg_pos(8, 0, 0b10101100)   #0xac

    def release_apc_low_table_gain(self):
        self.REG_LOW = '403440a0'
        self.write_reg_pos(15, 15, 0b0)   # tx_gain_dr_pulse
        self.write_reg_pos(14, 14, 0b0)     # tx_gain_dr
        # self.write_reg_pos(8, 0, 0b10101100)   #0xac

    def set_wf_pa_isense_en(self, val):
        self.REG_LOW = '40344044'
        self.write_reg_pos(12, 12, val)
        self.write_reg_pos(11, 9, 4)   #


    def set_wf_isense_input_sel_bit(self,val):
        self.REG_LOW = '40344044'
        self.write_reg_pos(8, 7, val)

    def set_pa_hb_gain_en_dr(self, val=0):
        self.REG_LOW = '40344004'
        self.write_reg_pos(31, 31, val)

    def set_pa_hb_gain_en_reg(self, val=0):
        self.REG_LOW = '40344004'
        self.write_reg_pos(30, 30, val)

    def set_pa_lb_gain_en_dr(self, val=0):
        self.REG_LOW = '40344004'
        self.write_reg_pos(29, 29, val)

    def set_pa_lb_gain_en_reg(self, val=0):
        self.REG_LOW = '40344004'
        self.write_reg_pos(28, 28, val)

    def set_wf_pa_vl_calbit(self, val):
        self.REG_LOW = '40344040'
        self.write_reg_pos(16, 11, val)

    def set_wf_pu_dtmx_wf_hb_dr(self, val):
        self.REG_LOW = '40344004'
        self.write_reg_pos(25, 25, val)

    def set_wf_pu_dtmx_wf_hb_reg(self, val):
        self.REG_LOW = '40344004'
        self.write_reg_pos(24, 24, val)


    def set_wf_pu_dtmx_wf_lb_dr(self, val):
        self.REG_LOW = '40344004'
        self.write_reg_pos(23, 23, val)

    def set_wf_pu_dtmx_wf_lb_reg(self, val):
        self.REG_LOW = '40344004'
        self.write_reg_pos(22, 22, val)


    def set_wf_test_enable_pa(self, en=0):
        self.REG_LOW = '40344008'
        self.write_reg_pos(5,5, en)

    def set_cm_test_enable_mdll(self, en=0):
        self.REG_LOW = '40505004'
        self.write_reg_pos(12,12, en)

    def set_cm_mdll_band_high_bit(self, val=0):
        self.REG_LOW = '4050500c'
        self.write_reg_pos(31, 30, val)

    def set_cm_mdll_freg_bit(self, val=0):
        self.REG_LOW = '4050500c'
        self.write_reg_pos(29, 27, val)

    def set_cfg_ana_test_mode(self, val=0):
        self.REG_LOW = '40502010'
        self.write_reg_pos(8, 7, val)

    def set_cfg_ana_test_bit(self, val=0):
        self.REG_LOW = '40502010'
        self.write_reg_pos(2, 0, val)

    def set_cfg_ana_io_test_bit(self, val=0):
        self.REG_LOW = '40502010'
        self.write_reg_pos(16, 13, val)

    def read_cfg_ana_test_bit(self):
        self.REG_LOW = '40502010'
        return self.read_reg_pos(2, 0)

    def set_cm_mdll_rstn(self, val=0):
        self.REG_LOW = '40505000'
        self.write_reg_pos(5, 4, val)

    def set_wf_vco_core_reg_lv_mode(self, val=0):
        self.REG_LOW = '40344070'
        self.write_reg_pos(0, 0, val)

    def set_wf_vco_core_reg_bit(self, val=0):
        self.REG_LOW = '40344070'
        self.write_reg_pos(5, 1, val)

    def set_wf_vco_buf_reg_hv_mode_bit(self, val=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(22, 21, val)

    def set_wf_vco_buf_reg_bit(self, val=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(26, 23, val)

    def set_wf_test_enable_vco(self, val=0):
        self.REG_LOW = '40344008'
        self.write_reg_pos(0, 0, val)

    def set_common_enable(self, addr, bit, en):
        """
        common_enable single bit set
        """
        self.REG_LOW = str(addr)
        self.write_reg_pos(bit, bit, en)

    def set_wf_enable_off(self):
        """
        all
        """
        self.REG_LOW = '40344008'
        self.write_reg_pos(31, 0, 0)

        # two cm_test_enable
        self.REG_LOW = '40505004'
        self.write_reg_pos(13, 12, 0)

        self.REG_LOW = '4034400c'
        self.write_reg_pos(29, 28, 0)

        self.REG_LOW = '40502010'
        self.write_reg_pos(4, 4, 0)

        self.REG_LOW = '40622004'
        self.write_reg_pos(12, 4, 0)


    def set_wf_test_enable_dtmx(self, val=0):
        self.REG_LOW = '40344008'
        self.write_reg_pos(4, 4, val)

    def set_txon(self, val=0):
        self.REG_LOW = '4034409c'
        self.write_reg_pos(3, 2, val)
        print('from  txon')

    def set_rxon(self, val=0):
        self.REG_LOW = '4034409c'
        self.write_reg_pos(1, 0, val)
        print('from  rxon')


    def set_wf_trx_rsvd_bit_3(self, val=0):
        self.REG_LOW = '40344060'
        self.write_reg_pos(3, 3, val)

    def set_lo_rsvd_bit_3(self, val=0):
        self.REG_LOW = '40344078'
        self.write_reg_pos(27, 27, val)

    def set_wf_dtmx_logen_dll_reg_vbit(self, val=0):
        self.REG_LOW = '40344050'
        self.write_reg_pos(15, 12, val)

    def set_wf_dtmx_loreg_vbit(self, val=0):
        self.REG_LOW = '40344050'
        self.write_reg_pos(23, 21, val)

    def set_wf_vco_core_psw_bit(self, val=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(31, 27, val)
        print('from  vco_core_psw_bit')

    def set_wf_vco_isense_bit(self, val=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(3, 2, val)
        print('from  wf_vco_isense_bit')

    def set_wf_vco_isense_en(self, en=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(1, 1, en)
        print('from  wf_vco_isense_en')

    def set_wf_vco_isense_volt_div_en(self, en=0):
        self.REG_LOW = '40344074'
        self.write_reg_pos(0, 0, en)

    def set_rtc_rg_dcdc_ldo_rf_mode_sel(self, en=0):
        self.REG_LOW = '70001000'
        self.write_reg_pos(0, 0, en)

    def set_pll_vco_band_reg(self, val=0):
        self.REG_LOW = '4034201c'
        self.write_reg_pos(12, 0, val)
        print('from  pll_vco_band_reg')

    def set_wf_vco_band_aux_bit(self, val=0):
        self.REG_LOW = '40344070'
        self.write_reg_pos(16, 15, val)
        print('from  vco_band_aux_bit')

    def ms_portdc_config(self):
        self.REG_LOW = '40100038'
        self.write_reg_pos(8, 8, 1)
        self.write_reg_pos(7, 0, 40)
        print('from  clkdiv')
        self.REG_LOW = '4010d008'
        self.write_reg_pos(27, 16, 512)
        self.write_reg_pos(3, 0, 0)
        self.write_reg_pos(28, 28, 1)


        print('from  winAddr')
        self.REG_LOW = '4010d00c'
        self.write_reg_pos(28, 27, 1)
        self.write_reg_pos(26, 25, 1)
        self.write_reg_pos(24, 21, 0)
        self.write_reg_pos(18, 15, 0b1101)
        self.write_reg_pos(14, 12, 2)
        self.write_reg_pos(1, 1, 0)

        self.write_reg_pos(20, 19, 1)
        self.write_reg_pos(10, 10, 1)
        self.write_reg_pos(9, 2, 121)

        self.write_reg_pos(11, 11, 0)
        self.write_reg_pos(0, 0, 0)
        print('from  anaAddr')

    def set_wf_rmx_super_het_en(self, en):
        self.REG_LOW = '40344020'
        self.write_reg_pos(19, 19, en)
        print('from  wf_rmx_super_het')

    def set_wf_pu_rmx_superhet_dr(self, val):
        self.REG_LOW = '40344000'
        self.write_reg_pos(15, 14, val)
        # print('from  wf_rmx_super_het')

    def set_bt_txon(self):
        self.REG_LOW = '40622044'
        self.write_reg_pos(15, 12, 0b1110)

    def set_bt_rxon(self):
        self.REG_LOW = '40622044'
        self.write_reg_pos(15, 12, 0b1011)

    def set_usb(self):
        self.REG_LOW = '40241004'
        self.write_reg_pos(28, 28, 1)
        self.write_reg_pos(26, 26, 1)

        self.REG_LOW = '4024100C'
        self.write_reg_pos(25, 22, 0b1111)
        self.write_reg_pos(17, 14, 0b1111)

    def set_bt_vco_core_reg_bit(self, val):
        self.REG_LOW = '40622034'
        self.write_reg_pos(19, 16, val)

    def set_apc_wf_dtmx_dac_vl_it_bit(self, addr_high, val):
        self.REG_HIGH = addr_high
        self.wapc(42, 37, val)

    def set_apc_wf_dtmx_dac_vl_ib_bit(self, addr_high, val):
        self.REG_HIGH = addr_high
        self.wapc(36, 32, val)

    def get_rate_table(self):
        self.REG_LOW = '403422c8'
        rate_table = self.read_reg_pos(13, 12)
        return int(rate_table, 2)

    def get_analog_gear(self):
        self.REG_LOW = '403422c8'
        rate_table = self.read_reg_pos(11, 8)
        return int(rate_table, 2)

    def get_txgain_page(self):
        self.REG_LOW = '40344094'
        txgain_page = self.read_reg_pos(16, 14)
        return int(txgain_page, 2)



if __name__ == "__main__":
    # global_create()
    print(int('79', 16))

    UART2 = Uart(4, wr_mode=True)
    UART2.set_baudrate("921600")
    UART2.open()
    swMode(UART2)
    ## val=UART2.sendcmd("r 403440ac")
    value=rapc(UART2,35,28)
    # print(value)
    # value=wapc(UART2,33,30,1000)
    wapc(UART2,35,29,0b1010101)
    hwMode(UART2)
    UART2.close()


