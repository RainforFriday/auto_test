from Bin import *


if __name__ == "__main__":

    old_apc_xlsx = "./aic8822/20240830/AIC8822_APC_LB_0822.xlsx"
    new_apc_xlsx = "./aic8822/20240830/AIC8822_APC_LB_0822_B03_D01_E01_F01.xlsx"
    old_bin = "./aic8822/20240830/testmode_8822_0822.bin"
    new_bin = "./aic8822/20240830/testmode_8822_0822_B03_D01_E01_F01.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("OFDM_H")
    # print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "OFDM_H")
