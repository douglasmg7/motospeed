#!/usr/bin/env python3

import sys
import logging
import datetime as dt
import os

LOG_PATH = os.path.join(os.environ['ZUNKAPATH'], 'log', 'handytech') 
LOG_FILE = os.path.join(LOG_PATH, 'handytech.log')
if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)

class MyFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp

    err_fmt = '%(asctime)s %(name)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
    default_fmt = '%(asctime)s %(name)s [%(levelname)s] %(message)s'

    def __init__(self):
        super().__init__(fmt=MyFormatter.default_fmt, datefmt='%Y/%m/%d %H:%M:%S.%f', style='%')

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt
        # Replace the original format with one customized by logging level
        if record.levelno == logging.ERROR:
            self._style._fmt = MyFormatter.err_fmt
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result

# change level name
logging.addLevelName(logging.DEBUG, 'debug')
logging.addLevelName(logging.INFO, 'info')
logging.addLevelName(logging.WARN, 'warning')
logging.addLevelName(logging.ERROR, 'error')
logging.addLevelName(logging.CRITICAL, 'critical')

# config
logger = logging.getLogger('[handytech]')
logger.setLevel(logging.DEBUG)
formatter = MyFormatter()

# console
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# file
fileHandler = logging.FileHandler(LOG_FILE)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

# short names
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical

#  # test
#  logger.debug('Debug message')
#  logger.info('Info message')
#  logger.warning('Warning message')
#  logger.error('Error message')
#  logger.critical('Critical message')
