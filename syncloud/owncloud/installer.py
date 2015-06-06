import os
from os.path import join
import shutil
from subprocess import check_output
import pwd

import psycopg2
from syncloud.insider.facade import get_insider
from syncloud.sam.installer import Installer as SamInstaller
from syncloud.sam.manager import get_sam
from syncloud.systemd.systemctl import remove_service, add_service
from syncloud.tools import app
import massedit
from syncloud.tools.nginx import Nginx

from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'
SYSTEMD_POSTGRESQL = 'owncloud-postgresql'


class OwncloudInstaller:
    def __init__(self):
        self.sam = get_sam()
        self.sam_installer = SamInstaller()

    def install(self, from_file=None):

        self.sam_installer.install('owncloud', from_file)

        config = Config()

        try:
            pwd.getpwnam('owncloud')
        except KeyError:
            check_output(['/usr/sbin/useradd', '-r', '-s', '/bin/false', 'owncloud', '--home', config.data_dir()])

        lang = os.environ['LANG']
        if lang not in check_output(['locale', '-a']):
            print("generating locale: {0}".format(lang))
            fix_locale_gen(lang)
            check_output('locale-gen')

        app_data_dir = app.get_app_data_root('owncloud', 'owncloud')

        app.create_data_dir(app_data_dir, 'config', 'owncloud')
        app.create_data_dir(app_data_dir, 'data', 'owncloud')

        print("setup crontab task")
        cron = OwncloudCron(config)
        cron.create()

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)

        with psycopg2.connect(database="postgres", user="owncloud", host="/tmp") as conn:
            with conn.cursor() as curs:
                print("creating owncloud database")
                curs.execute('ALTER USER owncloud WITH PASSWORD \'owncloud\';')

        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

        Nginx().add_app('owncloud', config.port())

    def remove(self):

        config = Config()
        Nginx().add_app('owncloud', config.port())
        cron = OwncloudCron(config)
        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)

        cron.remove()

        if os.path.isdir(config.install_path()):
            shutil.rmtree(config.install_path())


def fix_locale_gen(lang, locale_gen='/etc/locale.gen'):
    massedit.edit_files([locale_gen], ["re.sub('# {0}', '{0}', line)".format(lang)], dry_run=False)
