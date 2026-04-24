
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import os
import re
from collections import defaultdict
from itertools import cycle

def convert_labels(labels):
    """
    将标签中的数字后缀转换为描述性后缀
    _1 -> _before_ant0
    _2 -> _after_ant0
    _3 -> _before_ant1
    _4 -> _after_ant1
    """
    mapping = {
        '_1': '_before_ant0',
        '_2': '_after_ant0',
        '_3': '_before_ant1',
        '_4': '_after_ant1'
    }

    converted = []
    for label in labels:
        # 精确匹配后缀（确保是最后一个下划线后的数字）
        for suffix, replacement in mapping.items():
            if label.endswith(suffix):
                # 替换最后一个匹配的后缀
                new_label = label[:-len(suffix)] + replacement
                converted.append(new_label)
                break
        else:
            # 如果没有匹配的后缀，保持原样
            converted.append(label)

    return converted

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
        if line.startswith('cal '):
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
            # label = current_am_type if block_count[current_am_type] == 1 else f'{current_am_type}_2'
            label = f'{current_am_type}_{block_count[current_am_type]}'
            label = convert_labels([label])[0]
            data[label].append((am_begin, am_back))

    return data

# file_path = "dpd0807.log"  # 替换为你的文件路径
file_path = r"D:\Aic8800\8819\Log\test-38.5.txt"  # 替换为你的文件路径
# file_path = r"D:\Aic8800\8819\Log\dpd0808.log"  # 替换为你的文件路径
filename_with_ext = os.path.basename(file_path)  # "dpd0808.log"

# 2. 去除扩展名
file_name = os.path.splitext(filename_with_ext)[0]  # "dpd0808"


with open(file_path, "r", encoding="utf-8") as f:
    log_text = f.read()  # 读取整个文件内容


# 提取数据
extracted_data = extract_dpd_data(log_text)


# 提取需要绘制折线图的数据（am3, am5, am7, am9, ..., amd）
before_labels = [f'am{i}_1' for i in range(1, 16)]  # am1~am13
After_labels = [f'am{i}_2' for i in range(1, 16)]  # am1_2~am13_2

# 将10-13转换为字母后缀
for i in range(10, 16):
    before_labels[i-1] = f'am{chr(ord("a") + i - 10)}_1'      # 10→a, 11→b, etc.
    After_labels[i-1] = f'am{chr(ord("a") + i - 10)}_2'


plt.figure(figsize=(12, 6))

# plt.ion()

# 获取matplotlib默认的颜色循环
default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
print("默认颜色:", default_colors)
# 创建颜色循环器
color_cycler = cycle(default_colors)


# before_labels = ['amd_1', 'amd_3']
before_labels = convert_labels(before_labels)

for label in before_labels:
    if label in extracted_data:
        color = next(color_cycler)
        x = [point[0] for point in extracted_data[label]]
        y = [point[1] for point in extracted_data[label]]
        # plt.plot(x, y, label=label, marker='o')
        plt.plot(x, y, label=label, marker='.', linestyle='-', linewidth=2, color=color)
        # plt.draw()

# plt.xlabel('am_begin')
# plt.ylabel('am_back')
# plt.title('DPD Data: Line Plot (Primary)')
# plt.legend()
# plt.grid(True)
# plt.savefig('dpd_plot.png', dpi=300, bbox_inches='tight')
# plt.show()




# 提取需要绘制散点图的数据（am3_2, am5_2, am7_2, ..., amd_2）
# scatter_labels = ['am3_2', 'am5_2', 'am7_2', 'am9_2', 'amb_2', 'amc_2', 'amd_2']
# plt.figure(figsize=(12, 6))

color_cycler = cycle(default_colors)


# After_labels= ['amd_2', 'amd_4']
After_labels = convert_labels(After_labels)
for label in After_labels:
    if label in extracted_data:
        color = next(color_cycler)
        # 过滤掉y值为0的点
        points = [(x, y) for x, y in extracted_data[label] if y != 0]
        if points:  # 确保过滤后仍有数据
            x = [point[0] for point in points]
            y = [point[1] for point in points]
            # plt.scatter(x, y, label=label, alpha=0.7)
            # plt.plot(x, y, label=label, s=100, alpha=0.7, edgecolors='black')
            plt.plot(x, y, label=label, marker='^', linestyle='-', linewidth=2, color=color)

# plt.xlabel('am_begin')
# plt.ylabel('am_back')
# plt.title('DPD Data: Scatter Plot (Secondary, Non-Zero)')
# plt.legend()
# plt.grid(True)
# plt.savefig('dpd_scatter_plot.png', dpi=300, bbox_inches='tight')
# plt.show()

# 图表装饰
plt.xlabel('am_begin', fontsize=12)
plt.ylabel('am_back', fontsize=12)
plt.title(f'DPD Data: Point Plot (Primary) & Triangle Plot (After) From {filename_with_ext}', fontsize=14)
# plt.title('am{i}_1 and am{i}_2 is Ant0;  am{i}_3 and am{i}_4 is Ant1', fontsize=9, style='italic', pad=20)

# # 添加注释框
# note_text = '• am{i}_1 and am{i}_2 are Antenna 0 \n• am{i}_3 and am{i}_4 are Antenna 1'
# plt.annotate(note_text, xy=(0.98, 0.02), xycoords='figure fraction',
#             ha='right', va='bottom', fontsize=10,
#             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

# # 添加备注文本
# plt.figtext(0.86, 0.15, ' am{i}_1 and am{i}_2 is Ant0\n am{i}_3 and am{i}_4 is Ant1',
#            ha='center', fontsize=11, style='italic',
#            bbox={'facecolor': 'lightgray', 'alpha': 0.3, 'pad': 5})


# plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.legend(fontsize=10, loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# 保存图像
plt.savefig('analysis_'+file_name+'.png', dpi=300, bbox_inches='tight')
# plt.ioff()

plt.show()





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

