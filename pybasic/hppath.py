# encoding: utf-8
"""
@version: 0-0
@author: huangpeng
@contact: huangpeng@yahoo.com 
@site:    
@software: PyCharm
@file: pathlib.py
@time: 2019/9/16 16:53
"""

import os


class HpPath(object):
    def __init__(self, path_name=None):
        self.pathname = path_name

    def isabs(self):
        return os.path.isabs(self.abspath)

    def isexists(self):
        return os.path.exists(self.abspath)

    def islink(self):
        return os.path.islink(self.abspath)

    @staticmethod
    def __abspath(path):
        return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

    @property
    def abspath(self):
        return self.__abspath(self.pathname)

    @property
    def basename(self):
        return os.path.basename(self.abspath)

    @property
    def dirname(self):
        return os.path.dirname(self.abspath)

    @property
    def dirpath(self):
        return os.path.split(self.abspath)[0]


class LinuxPath(HpPath):
    def __init__(self, path_name):
        super(LinuxPath, self).__init__(path_name)
        self.path = self.pathname

    @property
    def owner(self):
        stat_info = os.stat(self.path)
        uid = stat_info.st_uid
        user = pwd.getpwuid(uid)[0]
        return user

    @property
    def grp(self):
        stat_info = os.stat(self.path)
        gid = stat_info.st_gid
        group = grp.getgrgid(gid)[0]
        return group

    def chown(self):
        pass

    def chgrp(self):
        pass

    def chmod(self):
        pass


if __name__ == "__main__":
    pass
