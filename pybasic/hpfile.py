import os
import shutil
from pybasic.hplog import *
from pybasic.hppath import *
from pybasic.hpdecor import *


class HpFile(HpPath):
    def __init__(self, path=None):
        super(HpFile, self).__init__(path)
        self.path = self.abspath

    def isexists(self):
        return os.path.isfile(self.path)

    @property
    def name(self):
        return self.basename

    @property
    def extname(self):
        return os.path.splitext(self.abspath)[-1]

    @decor_check_action
    def rename(self, name):
        os.rename(self.path, os.path.join(self.dirname, name))

    @decor_check_action
    def copy(self, dst_file):
        shutil.copyfile(self.path, dst_file)

    @decor_check_action
    def delete(self):
        os.remove(self.path)

    @decor_check_action
    def move(self, dst_file):
        shutil.move(self.path, dst_file)


class TxtFile(HpFile):
    def __init__(self, file_path):
        super(TxtFile, self).__init__(file_path)

    @decor_check_action
    def write(self, content_list=None):
        if content_list is None:
            content_list = []
        with open(self.path, "w") as FILE:
            for line in content_list:
                FILE.write(line)

    @decor_check_action
    def __read__(self):
        result = []
        with open(self.path, "r") as XFile:
            for line in XFile:
                result.append(line.strip())
        return result


if __name__ == "__main__":
    filePath = r".\hpcmd.py"
    cshFile = TxtFile(filePath)
    print(cshFile.__read__())
    # print(cshFile.path)
    # """
