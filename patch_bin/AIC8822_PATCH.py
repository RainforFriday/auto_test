from Bin import *


if __name__ == "__main__":

    old_apc_xlsx = "./aic8822/AIC8822_APC_LB_0618.xlsx"
    new_apc_xlsx = "./aic8822/AIC8822_APC_LB_0620.xlsx"
    old_bin = "./aic8822/testmode_8822_0619_2g4_1.bin"
    new_bin = "./aic8822/testmode_8822_0620.bin"

    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "OFDM_H")
