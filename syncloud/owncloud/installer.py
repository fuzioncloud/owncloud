import os
import shutil
import tarfile
from os.path import isfile, join
from subprocess import check_output

from syncloud.insider.facade import get_insider
import wget

from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron


OWNCLOUD_ARCHIVE = 'syncloud-owncloud.tar.gz'
OWNCLOUD_ARCHIVE_TMP = '/tmp/{0}/'.format(OWNCLOUD_ARCHIVE)
SYSTEMD_NGINX_NAME = 'owncloud-nginx.service'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm.service'

SYSTEMD_DIR = join('/lib', 'systemd', 'system')


class Installer():
    def __init__(self):
        self.config = Config()
        self.SYSTEMD_NGINX_FILE = join(self.config.install_path(), 'config', SYSTEMD_NGINX_NAME)
        self.SYSTEMD_PHP_FPM_FILE = join(self.config.install_path(), 'config', SYSTEMD_PHP_FPM_NAME)
        self.cron = OwncloudCron(self.config)

    def install(self):

        if isfile(OWNCLOUD_ARCHIVE_TMP):
            os.remove(OWNCLOUD_ARCHIVE_TMP)

        url = 'http://apps.syncloud.org/{0}'.format(OWNCLOUD_ARCHIVE)
        out = '/tmp/{0}'.format(OWNCLOUD_ARCHIVE)
        print("saving {0} to {1}".format(url, out))
        filename = wget.download(url, out)

        print("extracting {0}".format(filename))
        tarfile.open(filename).extractall(self.config.root_path())

        print("setup crontab task")
        self.cron.remove()
        self.cron.create()

        print("setup systemd")
        shutil.copy(self.SYSTEMD_NGINX_FILE, SYSTEMD_DIR)
        shutil.copy(self.SYSTEMD_PHP_FPM_FILE, SYSTEMD_DIR)

        check_output('systemctl enable -f {0}'.format(SYSTEMD_PHP_FPM_NAME), shell=True)
        check_output('systemctl enable -f {0}'.format(SYSTEMD_NGINX_NAME), shell=True)

        check_output('systemctl daemon-reload', shell=True)

        check_output('systemctl start {0}'.format(SYSTEMD_PHP_FPM_NAME), shell=True)
        check_output('systemctl start {0}'.format(SYSTEMD_NGINX_NAME), shell=True)

    def remove(self):

        check_output('systemctl stop {0}'.format(SYSTEMD_NGINX_NAME), shell=True)
        check_output('systemctl stop {0}'.format(SYSTEMD_PHP_FPM_NAME), shell=True)

        if os.path.isfile(join(SYSTEMD_DIR, self.SYSTEMD_NGINX_FILE)):
            os.remove(join(SYSTEMD_DIR, self.SYSTEMD_NGINX_FILE))

        if os.path.isfile(join(SYSTEMD_DIR, self.SYSTEMD_PHP_FPM_FILE)):
            os.remove(join(SYSTEMD_DIR, self.SYSTEMD_PHP_FPM_FILE))

        self.cron.remove()
        get_insider().remove_service(self.config.service_name())

        shutil.rmtree(self.config.install_path())
