from Bin import *

if __name__ == "__main__":
    old_apc_xlsx = "./aic8820/AIC8820H_APC_5G_MCS11_20240308.xlsx"
    new_apc_xlsx = "./aic8820/AIC8820H_APC_5G_MCS11_20240516.xlsx"
    old_bin = "./aic8820/testmode_8820_0620.bin"
    new_bin = "./aic8820/testmode_8820_0621.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("CH155")
    print(Binx.search_table(l_table))

    # bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "OFDM_H")
