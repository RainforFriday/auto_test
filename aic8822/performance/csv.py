import os
import sys


class CSV:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def write_append_line(self, line_string):
        with open(self.csv_path, "a+") as CSVFILE:
            if line_string.endswith("\n"):
                CSVFILE.write(line_string)
            else:
                CSVFILE.write(line_string + "\n")


if __name__ == "__main__":
    csv_path = "./test_csv.csv"
    csvx = CSV(csv_path)
    csvx.write_append_line("test,test,test1,tset2")
    csvx.write_append_line("test2,test,test1,tset2")
