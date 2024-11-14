from Bin import *

if __name__ == "__main__":
    old_apc_xlsx = "./aic8820H/20241113/AIC8820H_APC_5G_MCS11_20240708_V2.xlsx"
    new_apc_xlsx = "./aic8820H/20241113/AIC8820H_APC_5G_MCS11_20240708_V2_1.xlsx"
    old_bin = "./aic8820H/20241113/testmode20_2024_1112_2037.bin"
    new_bin = "./aic8820H/20241113/testmode20_2024_1112_2037_ch42_vbit1.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("CH42")
    # print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "CH42")
