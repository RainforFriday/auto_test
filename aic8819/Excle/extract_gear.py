import pandas as pd

# 读取数据
file_path = "aic8800_D40LC_test_cfg.xlsx"
df = pd.read_excel(file_path)

# 假设寄存器字符串在 "lvl" 列
lvl_data = df["lvl"]

analog_gear_list = []
apc_table_list = []

for entry in lvl_data:
    # 提取寄存器值（例：从 "r 403422c8  [0x403422C8] = 0x00FFDA89" 提取 00FFDA89）
    try:
        hex_str = entry.split("=")[-1].strip().replace("0x", "")
        reg_val = int(hex_str, 16)
    except Exception:
        analog_gear_list.append(None)
        apc_table_list.append(None)
        continue

    # 倒数第三位（16进制字符）
    if len(hex_str) >= 3:
        analog_gear = hex_str[-3].upper()
    else:
        analog_gear = None

    # 提取 bit[13:12]
    apc_table = (reg_val >> 12) & 0b11

    analog_gear_list.append(analog_gear)
    apc_table_list.append(apc_table)

# 保存结果到新Excel
result_df = pd.DataFrame({
    "analog_gear": analog_gear_list,
    "apc_table": apc_table_list
})

result_df.to_excel("parsed_registers.xlsx", index=False)
print("处理完成，结果已保存到 parsed_registers.xlsx")
