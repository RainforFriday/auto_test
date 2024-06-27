import sys
import time
import logging

fmt = '<%(asctime)s.%(msecs)03d>%(name)s.%(levelname)s: %(message)s'
datefmt = '%H:%M:%S'

def log2stdout(logger, level=logging.DEBUG, bhv='set'):
    assert isinstance(logger, logging.Logger), 'argument <1> is not logging.Logger instance'
    # add or set
    if(bhv[0] != 'a'):
        logger.handlers.clear()

    shdl = logging.StreamHandler(sys.stdout)
    shdl.setLevel(level)
    fmter = logging.Formatter(fmt, datefmt)
    shdl.setFormatter(fmter)
    logger.addHandler(shdl)
    logger.setLevel(level)

def log2file(logger, level=logging.DEBUG, name='', mode='w'):
    assert isinstance(logger, logging.Logger), 'argument <1> is not logging.Logger instance'
    # add or set
    #if(bhv[0] != 'a'):
    #    logger.handlers.clear()

    if not name:
        name = '{}_{}.log'.format(logger.name.strip(' _'), time.strftime('%Y%m%d_%H%M%S'))
    fhdl = logging.FileHandler(name, mode)
    fhdl.setLevel(level)
    fmter = logging.Formatter(fmt, datefmt)
    fhdl.setFormatter(fmter)
    logger.addHandler(fhdl)
    logger.setLevel(level)

