from MsPFM.aic8819_cal_ipa import *
import datetime
import csv

def get_dc(msadc0):
    raw_dc = msadc0.measure()
    dc1 = (int(raw_dc.split('x')[1], 16) * 1214 / 32896) - 1214
    return round(dc1, 2)


def volt_ms_robust_avg2(msadc0, avg_num=3, max_retries=3):
    """
    计算f(x)的稳健平均值，当单次测量偏差超过10%时重新获取数据

    参数：
        avg_num:
        max_retries: 最大重试次数

    返回：
        平均值, 有效测量次数
    """
    total_retries = 0
    valid_measurements = []

    while len(valid_measurements) < avg_num and total_retries < max_retries:
        # 获取新的一组3次测量
        current_measurements = []
        for _ in range(avg_num):
            current_measurements.append(get_dc(msadc0))
            print(f'Volt_i: {current_measurements[-1]}')

        # 检查偏差
        needs_retry = False
        if len(current_measurements) > 1:
            for i in range(1, len(current_measurements)):
                prev = current_measurements[i - 1]
                curr = current_measurements[i]
                if prev == 0:  # 避免除以零
                    deviation = float('inf')
                else:
                    deviation = abs(curr - prev) / abs(prev)

                if deviation > 0.15:  # 10%偏差
                    print(f"警告：测量偏差 {deviation * 100:.2f}% 超过阈值，重新测量...")
                    needs_retry = True
                    break

        if not needs_retry:
            valid_measurements.extend(current_measurements)

        total_retries += 1

    if not valid_measurements:
        # raise ValueError("无法获取有效测量数据")
        avg = sum(current_measurements) / len(current_measurements)
    else:
        avg = sum(valid_measurements) / len(valid_measurements)
    return round(avg, 3)



if __name__ == "__main__":

    hex_value = "C755"  # 16进制数据
    hex_value = "9F8A"  # 16进制数据
    dec_value = int(hex_value, 16)  # 转换为10进制
    result = (dec_value * 1214 / 32896) - 1214  # 计算公式

    print(f"16进制 '{hex_value}' → 10进制: {dec_value}")
    print(f"计算结果: {result}")



    # UARTc.open()
    UARTc=uart_open(8)
    apc_reg = ApcReg(UARTc)
    msadc0 = MSADC(clk_div=40, acc_mode=1)


    # apc_reg.REG_LOW = '40506008'
    # apc_reg.write_reg_pos(31, 0, 0x4338000)
    # apc_reg.REG_LOW = '40580018'
    # apc_reg.write_reg_pos(3, 0, 0x3)

    # apc_reg.fix_apc_high_table_gain()   # high rate table , fix c

    # apc_reg.set_wf_test_enable_pa(0)

    UARTc.sendcmd('w 40506008 4338000 ')
    UARTc.sendcmd('w 40580018 3 ')
    time.sleep(0.5)

    UARTc.sendcmd('w 40100038 128')
    UARTc.sendcmd('w 4010d008 02003000')
    UARTc.sendcmd('w 4010d00c 0a0ea5e5')
    UARTc.sendcmd('tc 0')

    # msadc0.ms_portdc_config()


    apc_reg.set_cm_test_enable_mdll(1)


    # get_dc(msadc0)

    # raw_dc1 =  (int(raw_dc.split('x')[1], 16) / self.Denom - 1) * 1214 * self.Mult / 1000.0


    current_time = datetime.datetime.now().strftime("%m%d_%H%M%S")

    file = r'./8819vco_' + current_time + ".csv"
    # info = 'pwr20; rate 5 0;testmode_8819h_0730.bin; 2nd board, 1st chip'
    with open(file, mode='a+', newline='') as csvfile:
        writer = csv.writer(csvfile)
        info = ['Info:'] + ['ch 100'] + ['testmode_8819h_0730.bin'] + ['8819'] + ['No.7 board']
        writer.writerow(info)
        writer.writerow([])  # 写入空行
        writer.writerow([])  # 写入空行
        header0 = ['cm_mdllband_high_bit'] + ['cm_mdll_freg_bit'] + ['name'] + ['ana_test_bit'] + ['voltage(mV)'] + \
                  ['name'] + ['ana_test_bit'] + ['voltage(mV)'] + ['name'] + ['ana_test_bit'] + ['voltage(mV)'] + \
                  ['name'] + ['ana_test_bit'] + ['voltage(mV)']
        writer.writerow(header0)



    apc_reg.set_cfg_ana_test_mode(2)
    UARTc.sendcmd('w 40328068 0')

    # for outer in range(2, 4):  # 外循环2到3
    #     apc_reg.set_cm_mdll_band_high_bit(outer)
    #     for inner in range(1, 8):  # 内循环1到7
    #         apc_reg.set_cm_mdll_freg_bit(inner)

    ch_list = []
    UARTc.sendcmd('setch ')


    UARTc.sendcmd('tc 0')
    print('------------------------------')
    print('寄存器：', apc_reg.read_reg_pos(31, 27))

    apc_reg.set_cm_mdll_rstn(2)
    apc_reg.set_cm_mdll_rstn(3)
    apc_reg.set_cfg_ana_test_bit(3)
    mdll_cp_out0 = volt_ms_robust_avg2(msadc0, 3)

    apc_reg.set_cm_mdll_rstn(2)
    apc_reg.set_cm_mdll_rstn(3)
    apc_reg.set_cfg_ana_test_bit(2)
    mdll_cp_out1 = volt_ms_robust_avg2(msadc0, 3)

    apc_reg.set_cm_mdll_rstn(2)
    apc_reg.set_cm_mdll_rstn(3)
    apc_reg.set_cfg_ana_test_bit(1)
    avdd_logic = volt_ms_robust_avg2(msadc0, 3)

    apc_reg.set_cm_mdll_rstn(2)
    apc_reg.set_cm_mdll_rstn(3)
    apc_reg.set_cfg_ana_test_bit(0)
    avdd_sw_mdll = volt_ms_robust_avg2(msadc0, 3)

    results = "{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
        outer, inner, "md11_cp_out0", 3, mdll_cp_out0, "md11_cp_out1", 2, mdll_cp_out1,
        "avdd_logic", 1, avdd_logic, "avdd_sw_mdll", 0, avdd_sw_mdll)

    with open(file, "a+") as CSVFILE:
        if results.endswith("\n"):
            CSVFILE.write(results)
        else:
            CSVFILE.write(results + "\n")
    # self.CSVX.write_append_line(results)
    print(results)




    # msadc0.portdc_bit(7)
    # msadc0.portdc_mode(2)

    # cal_ipa_v1 = volt_ms_robust_avg(3)




    uart_close()

