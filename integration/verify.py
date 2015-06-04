import logging
from os.path import dirname

from syncloud.app import logger

from syncloud.owncloud.installer import OwncloudInstaller
from syncloud.owncloud.setup import Setup

DIR = dirname(__file__)

def test_owncloud():
    logger.init(logging.DEBUG, True)

    OwncloudInstaller().install('owncloud.tar.gz')

    setup = Setup()
    assert not setup.is_finished()
    setup.finish('test', 'test')
    assert setup.is_finished()