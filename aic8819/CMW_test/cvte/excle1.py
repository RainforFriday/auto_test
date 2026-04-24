import pandas as pd
import os

def extract_and_save_to_new_sheet(input_file, output_file):
    # 确保目标目录存在，如果不存在则创建
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and output_dir != '':
        os.makedirs(output_dir)

    # 读取 Excel 文件
    df = pd.read_excel(input_file, header=None)

    # 创建一个新的 DataFrame 来存储汇总数据
    new_data = pd.DataFrame()

    # 提取 H2, H29, H56, ..., H28 + 27*i
    for i in range(27):
        # 获取每列数据：H2, H29, H56 ... 对应的行是 2, 29, 56 ...
        column_data = df.iloc[1 + i * 27:28 + i * 27, 7].reset_index(drop=True)  # 7是H列的索引
        new_data[f'Column_{i+1}'] = column_data

    # 保存到新的工作表
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        new_data.to_excel(writer, index=False)


# 使用示例
input_file = 'data.xlsx'  # 输入文件路径
output_file = 'output_data.xlsx'  # 输出文件路径

extract_and_save_to_new_sheet(input_file, output_file)
