# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@aicsemi.com 
@site:
@python: 3.7.4
@software: PyCharm
@file: excel.py
@time: 2019/8/7 13:35
"""

import os
import sys
from pybasic.hplog import *
# from openpyxl import load_workbook, workbook
# from openpyxl.styles import PatternFill
import xlwings as xw


class HpXlw:
    def __init__(self, excel_file_path):
        self.path = excel_file_path
        # self.red_fill = PatternFill("solid", fgColor="FF0000")
        try:
            self.app = xw.App(visible=False, add_book=False)
            self.work_book = self.app.books.open(self.path)
        except Exception as e:
            pass
        # self.color = self.color_list()

    def color_list(self):
        c_list = []
        for i in range(8):
            for j in range(8):
                for k in range(8):
                    c_list.append((i*32, j*32, k*32))
        return c_list

    def rc2pos(self, row, column):
        az = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return str(list(az)[column-1])+str(row)

    @property
    def sheet_names(self):
        names = []
        for sheet in self.work_book.sheets:
            names.append(sheet.name)
        return names

    def sheet_maxrow(self, sheet_name):
        return self.work_book.sheets[sheet_name].used_range.last_cell.row

    def sheet_maxcol(self, sheet_name):
        return self.work_book.sheets[sheet_name].used_range.last_cell.column

    def read_sheet_list(self, sheet_name):
        # return: content as a list
        try:
            content_list = []
            sheet = self.work_book[sheet_name]
            max_row = sheet.max_row
            max_col = sheet.max_column
            for row in range(1, max_row+1):
                row_list = []
                for col in range(1, max_col+1):
                    row_list.append(sheet.cell(row, col).value)
                content_list.append(row_list)
            return content_list
        except Exception as e:
            wlogerror(e)
            wlogerror("Read sheet Error: "+sheet_name)

    def write_cell(self, sheet_name, cell_row, cell_col, cell_value):
        try:
            sheet = self.work_book[sheet_name]
            sheet.cell(cell_row, cell_col).value = cell_value
            self.work_book.save(self.path)
        except Exception as e:
            wlogerror(e)

    def read_cell(self, sheet_name: str, cell_row, cell_col) -> str:
        try:
            return self.work_book[sheet_name].cell(cell_row, cell_col).value
        except Exception as e:
            wlogerror(e)

    def set_cell_color(self, sheet_name, cell_row, cell_col, color_s):
        try:
            self.work_book.sheets[sheet_name].range(self.rc2pos(cell_row, cell_col)).color = color_s
            # self.work_book.save(self.path)
        except Exception as e:
            wlogerror(e)

    def close(self):
        self.work_book.save()
        self.work_book.close()
        self.app.quit()


if __name__ == "__main__":
    excel_file = r"E:\scratch\aaa.xls"
    EXCEL1 = HpXlw(excel_file)
    aaa = EXCEL1.sheet_names[0]
    EXCEL1.set_cell_color(aaa, 1, 1, (255, 255, 255))
    # print(EXCEL1.rc2pos(1,1))
    # aaa = EXCEL1.sheet_names[0]
    # print(EXCEL1.sheet_maxrow(EXCEL1.sheet_names[0]))
    # print(EXCEL1.sheet_maxcol(EXCEL1.sheet_names[0]))
    # sheetNames = EXCEL1.sheet_names
    # sheet_name = sheetNames[0]
    # content = EXCEL1.read_sheet(sheet_name)
    # print(content)
    # content = EXCEL1.read()
    EXCEL1.close()
