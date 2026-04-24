import os
import sys

global GX


class GlobalVar:
    def __init__(self):
        self.global_dict = {}

    def set_value(self, key, value):
        self.global_dict[key] = value

    def get_value(self, key):
        try:
            return self.global_dict[key]
        except:
            print("Error: Get {} value error!!!".format(key))


def global_create():
    global GX
    GX = GlobalVar()