####################################################################################
# ##   MODFIY RECORD BY HUANGPENG
# ##   1, ADD FUNCTION: logexc()/wlogexc --used after in except:---> for record exception information   @20180909
# ##   2, ADD FUNCTION: log_midstr
# ##                    log_INIT/log_INFO/log_DEBUG/log_WARN/log_ERROR
# ##                    logdebug_pref/loginfo_pref/logwarn_pref/logerror_pref
# ##                    BY huangpeng @ 20181124
###
###
###
###################################################################################
# ## 1 update @ 20190417


import os
import logging
import time
import sys
import traceback

global log     # console type log
global logf    # log thant includes console and file type
global logfile  # file type log handler
global NUMSTR 


########################################################
#
# initilization process
########################################################
try:
    log = logging.getLogger('AIC')
    console = logging.StreamHandler()
    log.addHandler(console)
    log.setLevel(logging.INFO)
    # print('Load Log system, Log level: INFO!!!')
except Exception as e:
    print(e)
    print('Fail to load LOG SYSTEM!!!!!')
    print(traceback.format_exc())


#######################################################
def loggetlevel():
    global log
    loglvl = log.getEffectiveLevel()
    return logging.getLevelName(loglvl)


def logsetlevel(infolvl):
    global log
    if infolvl == 'DEBUG':
        log.setLevel(logging.DEBUG)
    elif infolvl == 'INFO':
        log.setLevel(logging.INFO)
    elif infolvl == 'WARN' or infolvl == 'WARNING':
        log.setLevel(logging.WARN)
    elif infolvl == 'ERROR':
        log.setLevel(logging.ERROR)
    elif infolvl == 'CRITICAL':
        log.setLevel(logging.CRITICAL)
    else:
        print('Error in level,try again...')
    
    # print 'LOG LEVEL set to:',loggetlevel();


def loginfo(info):
    global log
    log.info(info)


def logdebug(info):
    global log
    log.debug(info)


def logwarn(info):
    global log
    log.warn(info)


def logerror(info):
    global log
    log.error(info)


def logcritical(info):
    global log
    log.critical(info)


def logexc():
    global log
    # log.critical(str(sys.exc_info()))
    log.error(traceback.format_exc())


########################################################
#
# LOG File operation
########################################################
def logf_create(logname, Formatter=True):
    global logf
    global logfile

    # add console output method
    # logconsole=logging.StreamHandler();
    # logf.addHandler(logconsole);

    # creat log dir
    # createdir()
    [pathdir, name] = os.path.split(logname)
    if not os.path.exists(pathdir):
        try:
            os.makedirs(pathdir)
            logdebug("Create Dir: "+pathdir)
            logdir = pathdir
        except Exception as e:
            logexc()
            logerror("Create Dir Failed:"+pathdir)
            sys.exit(0)
        
    # add log file record method
    # logtime= time.strftime('_%Y_%m_%d_%H_%M_%S',time.localtime());
    filename = os.path.join(pathdir, name)
    logfile = logging.FileHandler(filename, 'a')
    logfile.setLevel(logging.INFO)
    if Formatter:
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        #formatter = logging.Formatter("")
        logfile.setFormatter(formatter)
    logf = logging.getLogger('AIC')
    logf.addHandler(logfile)

    logfsetlevel("INFO")
    return filename


def logfsetlevel(infolvl):
    global logfile

    if infolvl == 'DEBUG':
        logfile.setLevel(logging.DEBUG)
    elif infolvl == 'INFO':
        logfile.setLevel(logging.INFO)
    elif infolvl == 'WARN' or infolvl == 'WARNING':
        logfile.setLevel(logging.WARN)
    elif infolvl == 'ERROR':
        logfile.setLevel(logging.ERROR)
    elif infolvl == 'CRITICAL':
        logfile.setLevel(logging.CRITICAL)
    else:
        print('Error in level,try again...')


def wlog(recordln):
    global logf
    global log
    try:
        logf.info(recordln)
    except Exception as e:
        loginfo(recordln)


def wlogwarn(recordln):
    global logf
    global log
    try:
        logf.warn(recordln)
    except Exception as e:
        logwarn(recordln)


def wlogct(recordln):
    global logf
    global log
    try:
        logf.critical(recordln)
    except Exception as e:
        logct(recordln)


def wlogerror(recordln):
    global logf
    global log
    try:
        logf.error(recordln)
    except Exception as e:
        logerror(recordln)


def wlogdebug(recordln):
    global logf
    global log
    try:
        logf.debug(recordln)
    except Exception as e:
        logdebug(recordln)


def wlogexc():
    global logf
    global log
    try:
        wlogdebug("### ERROR INFORMATION: ###")
        wlogdebug(traceback.format_exc())
    except Exception as e:
        logerror("### ERROR INFORMATION: ###")
        logerror(traceback.format_exc())


def closelog():	
    global logfile
    global logf
    logfile.flush()
    logfile.close()
    logf.removeHandler(logfile)
