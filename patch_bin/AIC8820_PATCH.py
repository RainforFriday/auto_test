from Bin import *

if __name__ == "__main__":
    old_apc_xlsx = "./aic8820/20240913/AIC8820T_FEMKCT8526H_APC_5G_MCS11_20240905.xlsx"
    new_apc_xlsx = "./aic8820/20240913/AIC8820T_FEMKCT8526H_APC_5G_MCS11_20240913_V1.xlsx"
    #old_bin = "./aic8820/testmode_8820_0708_vhvbit_0s.bin"
    old_bin = "./aic8820/20240913/testmode_8820_0913_fem.bin"
    new_bin = "./aic8820/20240913/testmode_8820_0913_fem_V1.bin"
    #new_bin = "./aic8820/testmode_8820_0812_wf_pa_vh_vbit_7_new.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("CH42")
    # print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "CH42")
