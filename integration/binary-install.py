#!/usr/bin/env python
import logging
from os.path import dirname, join, abspath

from syncloud.app import logger
from syncloud.owncloud.installer import OwncloudInstaller

APP_DIR = abspath(join(dirname(__file__), '..'))

logger.init(logging.DEBUG, True)

print("installing local binary build")
OwncloudInstaller().install(join(APP_DIR, 'owncloud.tar.gz'))
