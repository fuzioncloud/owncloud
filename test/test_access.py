from os.path import dirname, join
from mock import MagicMock
from syncloud.owncloud.access import Access
from syncloud.owncloud.config import Config

config_dir = join(dirname(__file__), '..', 'config')
config_file = join(config_dir, 'owncloud-ctl.cfg')


def test_access():
    access = Access(Config(filename=config_file), MagicMock(), MagicMock(), MagicMock())