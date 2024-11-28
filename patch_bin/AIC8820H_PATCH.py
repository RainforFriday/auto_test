from Bin import *

if __name__ == "__main__":
    old_apc_xlsx = "./aic8820H/20241119/AIC8820H_APC_5G_MCS11_20241119.xlsx"
    new_apc_xlsx = "./aic8820H/20241119/AIC8820H_APC_5G_MCS11_20241119_ch42.xlsx"
    old_bin = "./aic8820H/20241119/testmode_8820_1119_apc.bin"
    new_bin = "./aic8820H/20241119/testmode_8820_1119_apc_ch155.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("CH155")
    # print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "CH155")
