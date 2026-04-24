import pandas as pd
import glob
import os
import re


def collect_by_intv():

    # 读取 Excel 文件
    file_path = r'D:\PyProject\AIC_TEST\aic8819\CMW_test\aic8800_D40LC_test_all2.xlsx'

    xls = pd.ExcelFile(file_path)

    # 打印所有工作表的名称
    print(xls.sheet_names)

    # 如果存在 'all' 工作表，读取它
    if 'all' in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name='all', header=None)
        print(df.head())  # 查看前几行数据
    else:
        print("'all' 工作表不存在，请检查工作表名称")

    # 读取工作表 'all'
    df = pd.read_excel(file_path, sheet_name='all', header=None)
    # df = pd.read_excel(file_path)

    # 创建一个新的 DataFrame 用于存储 27 列数据
    new_data = pd.DataFrame()

    # 循环提取 H2, H29, H56, ..., H28*(i) 并添加到新的列中
    for i in range(27):
        # H2, H29, H56, ..., H2 + 27*i
        column_data = df.iloc[1 + i * 27:28 + i * 27, 7].reset_index(drop=True)  # 7是H列的索引
        new_data[f'Column_{i+1}'] = column_data

    # 将新的 DataFrame 写入到一个新的工作表
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        new_data.to_excel(writer, sheet_name='汇总数据', index=False)

    print("数据已成功汇总到新的工作表")


def concat_csv_in_folder(folder_path, output_path):
    # 获取文件夹内所有CSV文件路径
    files = glob.glob(os.path.join(folder_path, "*.csv"))

    # 使用正则表达式从文件名中提取数字部分进行排序
    files.sort(key=lambda x: int(re.search(r'\d+', os.path.basename(x)).group()))

    # 读取并拼接所有CSV文件
    df_list = []
    for file in files:
        df = pd.read_csv(file)
        df_list.append(df)

    # 合并所有DataFrame
    concatenated_df = pd.concat(df_list, ignore_index=True)

    # 保存到新的Excel文件
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        concatenated_df.to_excel(writer, index=False, sheet_name="Merged_Data")

    print(f"数据已成功拼接并保存到 {output_path}")


if __name__ == "__main__":

    collect_by_intv()


    # # 使用示例
    # folder_path = r"D:\PyProject\AIC_TEST\aic8819\CMW_test\data2"  # 修改为你的文件夹路径
    # output_path = "output_file.xlsx"  # 输出文件路径
    #
    # concat_csv_in_folder(folder_path, output_path)