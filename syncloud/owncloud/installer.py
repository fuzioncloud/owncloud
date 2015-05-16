import os
import shutil
import tarfile
from os.path import isfile
import massedit
from syncloud.tools.apt import Apt
import MySQLdb
from syncloud.insider.facade import get_insider
import wget
from pwd import getpwnam
from grp import getgrnam
from syncloud.owncloud import apache
from syncloud.owncloud.config import Config
from syncloud.owncloud.cron import OwncloudCron

OWNCLOUD_ARCHIVE = 'owncloud-8.0.3.tar.bz2'
OWNCLOUD_ARCHIVE_TMP = '/tmp/{0}/'.format(OWNCLOUD_ARCHIVE)


def install():

    config = Config()

    Apt().install(['php5-gd', 'php5-json', 'php5-mysql', 'php5-curl', 'php5-intl', 'php5-mcrypt', 'php5-imagick'])

    # con = MySQLdb.connect('localhost', 'root', 'root')
    # with con:
    #     cur = con.cursor()
    #     cur.execute("CREATE DATABASE IF NOT EXISTS owncloud")
    #     cur.execute("GRANT ALL PRIVILEGES ON owncloud.* TO 'owncloud'@'localhost' IDENTIFIED BY 'owncloud'")

    if isfile(OWNCLOUD_ARCHIVE_TMP):
        os.remove(OWNCLOUD_ARCHIVE_TMP)

    url = 'http://apps.syncloud.org/{0}'.format(OWNCLOUD_ARCHIVE)
    out = '/tmp/{0}'.format(OWNCLOUD_ARCHIVE)
    print("saving {0} to {1}".format(url, out))
    filename = wget.download(url, out)

    print("extracting {0}".format(filename))
    tarfile.open(filename).extractall('/opt')

    print("owncloud dir:")
    os.system('ls -la {0}'.format(config.install_path()))

    print("fixing apps permissions")
    os.chown(
        '{0}/apps'.format(config.install_path()),
        getpwnam(config.cron_user()).pw_uid,
        getgrnam(config.cron_user()).gr_gid)
    os.system('ls -la {0}/apps/'.format(config.install_path()))

    print("setup crontab task")
    cron = OwncloudCron(config)
    cron.remove()
    cron.create()

    print("fixing php.ini")
    fix_php_charset()
    fix_php_raw_post_data()

    print("recreate link for apache")
    apache.drop_link(config.apache_link())
    apache.create_link(config.install_path(), config.apache_link())


def remove():
    config = Config()
    shutil.rmtree(config.install_path())
    apache.drop_link(config.apache_link())
    (OwncloudCron(config)).remove()
    get_insider().remove_service(config.service_name())


def fix_php_charset(php_ini='/etc/php5/apache2/php.ini'):
    massedit.edit_files(
        [php_ini],
        ["re.sub('[;]default_charset.*=.*', 'default_charset = \"UTF-8\"', line)"], dry_run=False)


def fix_php_raw_post_data(php_ini='/etc/php5/cli/php.ini'):
    massedit.edit_files(
        [php_ini],
        ["re.sub('[;]always_populate_raw_post_data.*=.*', 'always_populate_raw_post_data = -1', line)"], dry_run=False)
