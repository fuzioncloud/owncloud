from grp import getgrnam
import os
from pwd import getpwnam
import shutil
from os.path import join

import MySQLdb
from subprocess import check_output
import psycopg2
import pwd
from syncloud.sam.installer import Installer as SamInstaller
from syncloud.sam.manager import get_sam
from syncloud.systemd.systemctl import remove_service, add_service
from syncloud.tools import app

from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron

DB_USER = 'postgres'

OWNCLOUD_ARCHIVE = 'syncloud-owncloud.tar.gz'
OWNCLOUD_ARCHIVE_TMP = '/tmp/{0}'.format(OWNCLOUD_ARCHIVE)

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'
SYSTEMD_POSTGRESQL = 'postgresql'


class OwncloudInstaller:
    def __init__(self):
        self.sam = get_sam()
        self.sam_installer = SamInstaller()

    def install(self, from_file=None):

        self.sam_installer.install('owncloud', from_file)

        config = Config()
        cron = OwncloudCron(config)

        app_data_dir = app.get_data_dir('owncloud')
        app_config_dir = join(app_data_dir, 'config')
        print("checking app config folder: {0}".format(app_config_dir))
        if not os.path.isdir(app_config_dir):
            print("creating app config folder")
            os.mkdir(app_config_dir)

            os.chown(app_config_dir,
                     getpwnam(config.cron_user()).pw_uid,
                     getgrnam(config.cron_user()).gr_gid)
        else:
            print("app config folder already exists")

        app_root = '/opt/app/owncloud/'
        database = '/opt/data/owncloud/database'
        if not os.path.isdir(database):
            check_output('{0}postgresql/bin/initdb {0}'.format(app_root, database), shell=True)
            check_output('chmod 700 {0}'.format(database), shell=True)
            check_output('chown -R postgres. {0}'.format(database), shell=True)

        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
               curs.execute('CREATE USER owncloud WITH PASSWORD \'owncloud\'')
               curs.execute('CREATE DATABASE owncloud TEMPLATE template0 ENCODING \'UNICODE\'')
               curs.execute('ALTER DATABASE owncloud OWNER TO owncloud')
               curs.execute('GRANT ALL PRIVILEGES ON DATABASE owncloud TO owncloud')

        try:
            pwd.getpwnam(DB_USER)
        except KeyError:
            check_output('useradd -r -s /bin/false {0}'.format(DB_USER))

        print("setup crontab task")
        cron.remove()
        cron.create()

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)
        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

    def remove(self):

        config = Config()
        cron = OwncloudCron(config)
        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)

        cron.remove()

        if os.path.isdir(config.install_path()):
            shutil.rmtree(config.install_path())

