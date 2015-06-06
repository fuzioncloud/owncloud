from grp import getgrnam
import os
from pwd import getpwnam
import shutil
from os.path import join

from subprocess import check_output
import pwd
import psycopg2
from syncloud.sam.installer import Installer as SamInstaller
from syncloud.sam.manager import get_sam
from syncloud.systemd.systemctl import remove_service, add_service
from syncloud.tools import app

from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron
import massedit

OWNCLOUD_ARCHIVE = 'syncloud-owncloud.tar.gz'
OWNCLOUD_ARCHIVE_TMP = '/tmp/{0}'.format(OWNCLOUD_ARCHIVE)

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

        app_data_dir = app.get_data_dir('owncloud')
        os.chown(app_data_dir, getpwnam('owncloud').pw_uid, getgrnam('owncloud').gr_gid)

        self.create_dir(app_data_dir, 'config', 'owncloud')
        self.create_dir(app_data_dir, 'data', 'owncloud')

        print("setup crontab task")
        cron = OwncloudCron(config)
        cron.create()

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)

        with psycopg2.connect(database="postgres", user="owncloud", host="/tmp") as conn:
            with conn.cursor() as curs:
                print("creating owncloud database")
                # curs.execute('CREATE USER owncloud WITH PASSWORD \'owncloud\'')
                curs.execute('ALTER USER owncloud WITH PASSWORD \'owncloud\';')
                # curs.execute('CREATE DATABASE owncloud TEMPLATE template0 ENCODING \'UNICODE\'')
                # curs.execute('ALTER DATABASE owncloud OWNER TO owncloud')
                # curs.execute('GRANT ALL PRIVILEGES ON DATABASE owncloud TO owncloud')

        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

    def create_dir(self, app_data_dir, dir_name, user):
        data_dir = join(app_data_dir, dir_name)
        print("checking app config folder: {0}".format(data_dir))
        if not os.path.isdir(data_dir):
            print("creating app data dir: {0}".format(data_dir))
            os.mkdir(data_dir)
            os.chown(data_dir, getpwnam(user).pw_uid, getgrnam(user).gr_gid)
        else:
            print("app data dir exists: {0}".format(data_dir))

    def remove(self):

        config = Config()
        cron = OwncloudCron(config)
        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)

        cron.remove()

        if os.path.isdir(config.install_path()):
            shutil.rmtree(config.install_path())

def fix_locale_gen(lang, locale_gen='/etc/locale.gen'):
    massedit.edit_files([locale_gen], ["re.sub('# {0}', '{0}', line)".format(lang)], dry_run=False)
