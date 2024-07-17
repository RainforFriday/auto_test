from Bin import *

if __name__ == "__main__":
    old_apc_xlsx = "./aic8820H/AIC8820H_APC_5G_MCS7_20240516.xlsx"
    new_apc_xlsx = "./aic8820H/AIC8820H_APC_5G_MCS7_20240717.xlsx"
    #old_bin = "./aic8820/testmode_8820_0708_vhvbit_0s.bin"
    old_bin = "./aic8820H/testmode20_2024_0712_2036.bin"
    new_bin = "./aic8820H/testmode20_2024_0717_ch122_c_vmref_6.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("CH155")
    #print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    # bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "CH122")
