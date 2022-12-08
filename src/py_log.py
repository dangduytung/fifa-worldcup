#!/usr/bin/env python
import sys
import os

import logging.config
from datetime import datetime

# root, dev
LOG_ENV = 'dev'
LOG_CONFIG_NAME = 'logging.conf'

# Folder save log file
FOLDER_SAVE_lOG = 'logs'
if not os.path.exists(FOLDER_SAVE_lOG):
    os.mkdir(FOLDER_SAVE_lOG)

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_path = os.path.join(application_path, LOG_CONFIG_NAME)

logging.config.fileConfig(config_path)
log = logging.getLogger(LOG_ENV)

fh = logging.FileHandler(FOLDER_SAVE_lOG + '\\' +
                         '{:%Y-%m-%d}.log'.format(datetime.now()), encoding="UTF-8")
formatter = logging.Formatter(
    '%(asctime)s | %(name)-4s | %(levelname)-8s | %(filename)s | %(lineno)04d | %(funcName)s | %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

# TEST
# log.info('test log info')
# log.debug('test log debug')
# log.warning('test log warning')
# log.error('test log error')