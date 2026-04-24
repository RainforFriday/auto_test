
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import os
import csv
import re
from collections import defaultdict


def extract_dpd_data(log_text):
    data = defaultdict(list)
    current_am_type = None
    block_count = defaultdict(int)
    reading_data = False  # 标记是否正在读取数据块

    # 正则表达式匹配数据行
    # data_pattern = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$')
    data_pattern = re.compile(r'^\s*(\d+)\s+(\d+)(?:\s+\S+)*\s*$')  # 只要求前两列是数字
    # 终止条件正则（匹配"dpd bypass status"或"i DPD_out DPD_pm_out"）
    stop_pattern = re.compile(r'^\s*(dpd|i DPD_out)\s*')

    for line in log_text.split('\n'):
        line = line.strip()
        if line.startswith('cal'):
            # 检测到新数据块，提取am类型（如3、5、7、9、b、d）
            am_type = line.split()[1]
            current_am_type = f'am{am_type}'
            block_count[current_am_type] += 1
            reading_data = True
        elif stop_pattern.match(line):
            # 检测到终止条件，停止读取当前数据块
            reading_data = False
        elif reading_data and data_pattern.match(line):
            # 提取am_begin和am_back
            am_begin, am_back = map(int, data_pattern.match(line).groups())
            label = current_am_type if block_count[current_am_type] == 1 else f'{current_am_type}_2'
            data[label].append((am_begin, am_back))

    return data


input_file = r"D:\Aic8800\8819\Log\evm_data.txt"
output_file = r"D:\Aic8800\8819\Log\evm_data.csv"

pwr_list = []
evm_list = []

# 用正则提取
pattern = re.compile(r"pwr:\s*([-+]?\d*\.?\d+)\s+evm:\s*([-+]?\d*\.?\d+)")

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            pwr = float(match.group(1))
            evm = float(match.group(2))
            pwr_list.append(pwr)
            evm_list.append(evm)

# 保存到 CSV
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["pwr", "evm"])  # 表头
    for pwr, evm in zip(pwr_list, evm_list):
        writer.writerow([pwr, evm])

print(f"已提取 {len(pwr_list)} 组数据并保存到 {output_file}")





#
# # file_path = "dpd0807.log"  # 替换为你的文件路径
# file_path = r"D:\Aic8800\8819\Log\evm"  # 替换为你的文件路径
# # file_path = r"D:\Aic8800\8819\Log\dpd0808.log"  # 替换为你的文件路径
# filename_with_ext = os.path.basename(file_path)  # "dpd0808.log"
#
# # 2. 去除扩展名
# file_name = os.path.splitext(filename_with_ext)[0]  # "dpd0808"
#
#
# with open(file_path, "r", encoding="utf-8") as f:
#     log_text = f.read()  # 读取整个文件内容
#
#
# # 提取数据
# extracted_data = extract_dpd_data(log_text)
#
# # 打印结果
# # for label, points in extracted_data.items():
# #     x = [point[0] for point in points]
# #     y = [point[1] for point in points]
# #     print(f"{label}: x={x}, y={y}")
#
#
#
# # 提取需要绘制折线图的数据（am3, am5, am7, am9, ..., amd）
# line_labels = [f'am{i}' for i in range(1, 14)]  # am1~am13
# scatter_labels = [f'am{i}_2' for i in range(1, 14)]  # am1_2~am13_2
#
# # 将10-13转换为字母后缀
# for i in range(10, 14):
#     line_labels[i-1] = f'am{chr(ord("a") + i - 10)}'      # 10→a, 11→b, etc.
#     scatter_labels[i-1] = f'am{chr(ord("a") + i - 10)}_2'
#
#
#
# plt.figure(figsize=(12, 6))
#
# for label in line_labels:
#     if label in extracted_data:
#         x = [point[0] for point in extracted_data[label]]
#         y = [point[1] for point in extracted_data[label]]
#         # plt.plot(x, y, label=label, marker='o')
#         plt.plot(x, y, label=label, marker='o', linestyle='-', linewidth=2)
#
# # plt.xlabel('am_begin')
# # plt.ylabel('am_back')
# # plt.title('DPD Data: Line Plot (Primary)')
# # plt.legend()
# # plt.grid(True)
# # plt.savefig('dpd_plot.png', dpi=300, bbox_inches='tight')
# # plt.show()
#
#
#
#
# # 提取需要绘制散点图的数据（am3_2, am5_2, am7_2, ..., amd_2）
# # scatter_labels = ['am3_2', 'am5_2', 'am7_2', 'am9_2', 'amb_2', 'amc_2', 'amd_2']
# # plt.figure(figsize=(12, 6))
#
# for label in scatter_labels:
#     if label in extracted_data:
#         # 过滤掉y值为0的点
#         points = [(x, y) for x, y in extracted_data[label] if y != 0]
#         if points:  # 确保过滤后仍有数据
#             x = [point[0] for point in points]
#             y = [point[1] for point in points]
#             # plt.scatter(x, y, label=label, alpha=0.7)
#             plt.scatter(x, y, label=label, s=100, alpha=0.7, edgecolors='black')
#
# # plt.xlabel('am_begin')
# # plt.ylabel('am_back')
# # plt.title('DPD Data: Scatter Plot (Secondary, Non-Zero)')
# # plt.legend()
# # plt.grid(True)
# # plt.savefig('dpd_scatter_plot.png', dpi=300, bbox_inches='tight')
# # plt.show()
#
# # 图表装饰
# plt.xlabel('am_begin', fontsize=12)
# plt.ylabel('am_back', fontsize=12)
# plt.title('DPD Data: Line Plot (Primary) & Scatter Plot (Secondary)', fontsize=14)
# plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.tight_layout()
#
# # 保存图像
# plt.savefig('analysis_'+file_name+'.png', dpi=300, bbox_inches='tight')
# plt.show()





#
#
# # 1. 读取 Excel 文件
# file_path = "amam.xlsx"  # 替换为你的文件路径
# df = pd.read_excel(file_path)
#
# # 2. 设置第一列为 x 轴，其他列为 y 轴
# x = df.iloc[:, 0]  # 第一列作为 x 轴
# y_columns = df.columns[1:]  # 其他列作为 y 轴
#
# # 3. 绘制折线图
# plt.figure(figsize=(12, 6))  # 设置图像大小
#
# for column in y_columns:
#     plt.plot(x, df[column], label=column)  # 绘制每条折线
#
# # 4. 添加图例和标签
# plt.xlabel(df.columns[0])  # x 轴标签（第一列名称）
# plt.ylabel("Value")        # y 轴标签
# plt.title("Multi-Line Chart from Excel Data")  # 图表标题
# plt.legend()              # 显示图例
# plt.grid(True)            # 显示网格
#
# # 5. 显示图表
# plt.show()

