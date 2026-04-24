from toolkit.PXA import *
from toolkit.ApcReg import *
from icbasic.aicintf.uart import *
# from toolkit.util import *


def uart_open(comport):
    global UARTc
    UARTc = Uart(comport)
    UARTc.open()
    return UARTc

def get_apc_addr(table: int, gain: int):
    base = 0x40348000
    addr_low = base + table * 0x80 + gain * 0x08
    addr_high = addr_low + 0x04
    return hex(addr_low).split('0x')[1], hex(addr_high).split('0x')[1]

def get_index_by_ch(ch):
    """
    根据ch值返回对应的index
    ch=7,42,58,106,122,138,155 对应 index=0,1,2,3,4,5,6
    """
    ch_to_index = {
        7: 0,
        42: 1,
        58: 2,
        106: 3,
        122: 4,
        138: 5,
        155: 6
    }

    return ch_to_index.get(ch, -1)  # 如果ch不在映射中，返回-1

def get_freq_by_ch(ch):
    # defalut unit : MHz
    if int(ch) < 15:
        freq = (2407 + 5 * int(ch))
    elif (int(ch) > 30) and (int(ch) < 170):
        freq = (5000 + 5 * int(ch))
    else:
        freq = int(ch)
    # self.sa.write("CONFigure:WLAN:MEAS{}:RFSettings:FREQuency {}".format(self.MeasNum, freq))
    return freq


def pwr_measure(ch):
    PXA_IP = "TCPIP0::K-N9030B-40540::hislip0::INSTR"
    pxa = PXA(PXA_IP)

    pxa.set_reflvl(30)
    pxa.set_rb(1)
    pxa.set_vb(3)
    pxa.set_span(300)

    freq = get_freq_by_ch(ch)
    pxa.set_cfreq(freq)
    mk_res = pxa.get_quick_peak_search(wait=2)[1]
    return mk_res




def cal_wf_dtmx_cbit_lb(ch=7, TMX_CBIT_PEAK_TYP=11):
    # step1: open band stream dpd path
    # step2: load low rate apc
    UARTc = uart_open(18)
    apc_reg = ApcReg(UARTc)

    UARTc.sendcmd('tc 0')
    UARTc.sendcmd('tone_off')
    apc_reg.release_apc_table_gain()

    rate_group_lst = [0, 1, 1, 1, 1, 1, 1]
    ch_group_lst = [0, 1, 2, 3, 4, 5, 6]
    index = get_index_by_ch(ch)
    UARTc.sendcmd(f'setch {ch}')
    time.sleep(2)


    # step3: set dig tone pwr, tone_on
    analog = 9
    if ch > 7:
        analog = 10
    fix_table = rate_group_lst[index] + ch_group_lst[index] * 3     # fix_table = rate_table + ch_group * 3
    fix_table_gain = (fix_table << 4) | analog
    print(hex(fix_table_gain))

    am = "4ff"
    UARTc.sendcmd(f'tone_on 4 {am} ' + str(hex(fix_table_gain)))


    # step4: fix analog gain index : 9
    apc_reg.fix_apc_table_gain(fix_table_gain)
    addrs = get_apc_addr(fix_table, analog)
    addr_high = addrs[1]


    # step5: cal wf_dtmx_cbit_lb
    tmx_pwr_peak = 0
    tmx_reg_peak = 0
    for cbit in range(0, 16, 2):
        apc_reg.set_apc_wf_dtmx_cbit_lb(addr_high, cbit)

        tmx_pwr = pwr_measure(ch)
        if tmx_pwr > tmx_pwr_peak:
            tmx_pwr_peak = tmx_pwr
            tmx_reg_peak = cbit

    tmx_cbit_offset = tmx_reg_peak - TMX_CBIT_PEAK_TYP
    # step7: update wf_dtmx_cbit_lb value in all apc and index;
    # apc include: 11b/ofdm_highrate/ofdm_lowrate
    # index include : 0~f
    cal_wf_lbSTREAM_padrv_cbit_new = wf_lbSTREAM_padrv_cbit_old + padrv_cbit_offset
    cal_wf_lbSTREAM_padrv_cbit_new = cal_wf_lbSTREAM_padrv_cbit_new > 16 ? 15: cal_wf_lbSTREAM_padrv_cbit_new
    cal_wf_lbSTREAM_padrv_cbit_new = cal_wf_lbSTREAM_padrv_cbit_new < 0 ? 0: cal_wf_lbSTREAM_padrv_cbit_new


    # cal done!
    # step 9: close tone
    # step 10: close dpd path
    apc_reg.release_apc_table_gain()
    UARTc.sendcmd('tone_off')
    UARTc.close()

    return {tmx_reg_peak, tmx_cbit_offset}






if __name__ == "__main__":

    ###
    """
    ch7:   cal_wf_dtmx_cbit_lb(ch=7, TMX_CBIT_PEAK_TYP=11)
    CH42:  cal_wf_dtmx_cbit_hb(ch=42, TMX_CBIT_PEAK_TYP=12)
    CH58:  cal_wf_dtmx_cbit_hb(ch=58, TMX_CBIT_PEAK_TYP=10)
    CH106: cal_wf_dtmx_cbit_hb(ch=106, TMX_CBIT_PEAK_TYP=7)
    CH122: cal_wf_dtmx_cbit_hb(ch=122, TMX_CBIT_PEAK_TYP=4)
    CH138: cal_wf_dtmx_cbit_hb(ch=138, TMX_CBIT_PEAK_TYP=0)
    CH155: cal_wf_dtmx_cbit_hb(ch=155, TMX_CBIT_PEAK_TYP=0)
    """




    if ch > 58:
        in_cbit = 0
        # for in_cbit in range(1, 3):
        apc_reg.set_apc_wf_pa_hb_input_cbit(addr_high, in_cbit)

    for bit in range(32):
    # for bit in [0, 1, 2] + list(range(5, 11, 3)):
    # for bit in range(0, 17, 4):
        if index < 2:
            apc_reg.set_apc_wf_dtmx_cbit_lb(addr_high, bit)
        else:
            apc_reg.set_apc_wf_dtmx_cbit_hb(addr_high, bit)
        mk_res = pxa.get_quick_peak_search(wait=2)
        # print(f'pwr: {mk_res[1]}   freq: {mk_res[0]}')



