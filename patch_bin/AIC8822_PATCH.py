from Bin import *


if __name__ == "__main__":

    old_apc_xlsx = "./aic8822/20241212/AIC8822_APC_LB_20241204_FEM_temporary.xlsx"
    new_apc_xlsx = "./aic8822/20241212/AIC8822_APC_LB_360FEM_20241212.xlsx"
    old_bin = "./aic8822/20241212/lmacfw_fem.bin"
    new_bin = "./aic8822/20241212/lmacfw_24G_apc.bin"

    Binx = Bin(old_bin)
    OLD_APCX = APCXLSX(old_apc_xlsx)
    l_table = OLD_APCX.read_table_to_list("11B")
    # print(l_table)
    print(Binx.search_table(l_table))

    # sheet_list = ["CH42", "CH58", "CH106", "CH122", "CH138", "CH155"]
    bin_replace_apc(old_apc_xlsx, new_apc_xlsx, old_bin, new_bin, "11B")
