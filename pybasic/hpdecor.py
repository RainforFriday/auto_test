# list:

import os
import sys
import datetime
from pybasic.hplog import *


def decor_measure_run_time(origin_func):
    def wrapper(*args, **kwargs):
        time_start = datetime.datetime.now()
        results = origin_func(*args, **kwargs)
        time_stop = datetime.datetime.now()
        time_used = time_stop - time_start
        wlogdebug("Total Time Used: "+str(time_used)+" seconds!")
        return results
    return wrapper


def decor_catch_exception(origin_func):
    def wrapper(*args, **kwargs):
        try:
            results = origin_func(*args, **kwargs)
            return results
        except Exception as e:
            wlogerror(e)
            return None
    return wrapper


def decor_check_action(origin_func):
    def wrapped(self, *args, **kwargs):
        try:
            origin_func(self, *args, **kwargs)
            return True
        except Exception as e:
            wlogerror(e)
            return False
    return wrapped


if __name__ == "__main__":
    pass
