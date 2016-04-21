from os.path import dirname, join, abspath, isdir
from os import listdir
import sys

from syncloud_platform.application import api
APP_NAME = 'owncloud'
USER_NAME = 'owncloud'

app_path = abspath(join(dirname(__file__), '..', '..', 'owncloud'))
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [join(lib_path, item) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(sys.path.append, libs)

app_setup = api.get_app_setup(APP_NAME)
app_storage_dir = app_setup.init_storage(USER_NAME)

from owncloud.installer import OwncloudInstaller
OwncloudInstaller().prepare_storage(app_storage_dir)
