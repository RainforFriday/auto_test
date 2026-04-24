###

import os
import shutil
from pybasic.hplog import *
from pybasic.hppath import *
from pybasic.hpdecor import *


class HpDir(HpPath):
    def __init__(self, path=None):
        super(HpDir, self).__init__(path)
        self.path = self.abspath

    @property
    def name(self):
        return self.basename

    def isexist(self):
        return os.path.isdir(self.path)

    @decor_check_action
    def create(self):
        os.makedirs(self.path)

    @decor_check_action
    def copy2dir(self, dst, symlinks=False):
        # copy tree
        # for example : self.path = /home/aaa/bbb/ccc
        #               dst = /test1/test2/test3
        #               copy{ dir: ccc----> dir: test3  }
        shutil.copytree(self.path, dst, symlinks)

    @decor_check_action
    def delete(self):
        shutil.rmtree(self.path)


if __name__ == "__main__":
    # """
    dir_path = r"./"
    Dir1 = HpDir(dir_path)
    print(Dir1.create())
    # Dir1.copy(r"E:\aaa")
    # for file_path in Dir1.find_dir("py"):
