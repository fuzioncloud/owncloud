from grp import getgrnam
import os
from pwd import getpwnam
import shutil
import tarfile
from os.path import isfile, join
from subprocess import check_output

import MySQLdb

from syncloud.sam.manager import get_sam
from syncloud.systemd.systemctl import remove_service, add_service
from syncloud.tools import app

import wget

from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron

OWNCLOUD_ARCHIVE = 'syncloud-owncloud.tar.gz'
OWNCLOUD_ARCHIVE_TMP = '/tmp/{0}'.format(OWNCLOUD_ARCHIVE)

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'


class Installer:
    def __init__(self):
        self.config = Config()
        self.cron = OwncloudCron(self.config)
        self.sam = get_sam()

    def install(self):

        if isfile(OWNCLOUD_ARCHIVE_TMP):
            os.remove(OWNCLOUD_ARCHIVE_TMP)
        arch = check_output('uname -m', shell=True).strip()
        url = 'http://apps.syncloud.org/{0}/{1}/{2}'.format(self.sam.get_release(), arch, OWNCLOUD_ARCHIVE)
        print("saving {0} to {1}".format(url, OWNCLOUD_ARCHIVE_TMP))
        filename = wget.download(url, OWNCLOUD_ARCHIVE_TMP)

        print("extracting {0}".format(filename))
        tarfile.open(filename).extractall(self.config.root_path())

        app_data_dir = app.get_data_dir('owncloud')
        app_config_dir = join(app_data_dir, 'config')
        print("checking app config folder: {0}".format(app_config_dir))
        if not os.path.isdir(app_config_dir):
            print("creating app config folder")
            os.mkdir(app_config_dir)
            os.chown(app_config_dir,
                     getpwnam(self.config.cron_user()).pw_uid,
                     getgrnam(self.config.cron_user()).gr_gid)
        else:
            print("app config folder already exists")

        print("setup database")
        con = MySQLdb.connect('localhost', 'root', 'root')
        with con:
            cur = con.cursor()
            cur.execute("CREATE DATABASE IF NOT EXISTS owncloud")
            cur.execute("GRANT ALL PRIVILEGES ON owncloud.* TO 'owncloud'@'localhost' IDENTIFIED BY 'owncloud'")

        print("setup crontab task")
        self.cron.remove()
        self.cron.create()

        print("setup systemd")
        add_service(self.config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(self.config.install_path(), SYSTEMD_NGINX_NAME)

    def remove(self):

        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)

        self.cron.remove()

        if os.path.isdir(self.config.install_path()):
            shutil.rmtree(self.config.install_path())

