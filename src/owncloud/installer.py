from os import symlink
from os.path import isdir, join, isfile
import shutil
import uuid
from subprocess import check_output

from syncloud_app import logger

from syncloud_platform.gaplib import fs, linux
from syncloud_platform.application import api

from owncloud.postgres import Database
from owncloud.config import Config
from owncloud.cron import OwncloudCron
from owncloud.occ import occ
from owncloud.occonfig import owncloud_config_set
from owncloud.webface import Setup

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'
SYSTEMD_POSTGRESQL = 'owncloud-postgresql'
INSTALL_USER = 'installer'
APP_NAME = 'owncloud'
USER_NAME = 'owncloud'
DB_NAME = 'owncloud'
DB_USER = 'owncloud'
PSQL_PATH = 'postgresql/bin/psql'

class OwncloudInstaller:
    def __init__(self):
        self.log = logger.get_logger('owncloud_installer')
        self.app = api.get_app_setup(APP_NAME)

    def install(self):

        config = Config()

        linux.fix_locale()

        linux.useradd(USER_NAME)

        fs.chownpath(self.app.get_install_dir(), USER_NAME, recursive=True)

        app_data_dir = self.app.get_data_dir()

        config_dir = join(app_data_dir, 'config')
        log_dir = join(app_data_dir, 'log')

        fs.makepath(config_dir)
        fs.makepath(log_dir)

        fs.chownpath(app_data_dir, USER_NAME, recursive=True)

        symlink(config_dir, config.owncloud_config_link())

        print("setup systemd")
        self.app.add_service(SYSTEMD_POSTGRESQL)
        self.app.add_service(SYSTEMD_PHP_FPM_NAME)
        self.app.add_service(SYSTEMD_NGINX_NAME)

        self.prepare_storage()

        if not self.installed():
            self.initialize(config)

        cron = OwncloudCron(config)
        cron.remove()
        cron.create()

        owncloud_config_set('memcache.local', '\OC\Memcache\APCu')
        owncloud_config_set('loglevel', '2')
        owncloud_config_set('logfile', config.log_file())
        owncloud_config_set('datadirectory', config.data_dir())
        owncloud_config_set('integrity.check.disabled', 'true')

        self.update_domain()

        fs.chownpath(config.app_data_dir(), USER_NAME, recursive=True)

        self.app.register_web(config.port())

    def remove(self):

        config = Config()
        self.app.unregister_web()
        cron = OwncloudCron(config)
        self.app.remove_service(SYSTEMD_NGINX_NAME)
        self.app.remove_service(SYSTEMD_PHP_FPM_NAME)
        self.app.remove_service(SYSTEMD_POSTGRESQL)

        cron.remove()

        if isdir(self.app.get_install_dir()):
            shutil.rmtree(self.app.get_install_dir())

    def installed(self):
        config = Config()
        if not isfile(config.config_file()):
            return False

        return 'installed' in open(config.config_file()).read().strip()

    def initialize(self, config):

        print("initialization")

        db_postgres = Database(join(self.app.get_install_dir(), PSQL_PATH), database='postgres', user=DB_USER)
        db_postgres.execute("ALTER USER owncloud WITH PASSWORD 'owncloud';")

        Setup().finish(INSTALL_USER, unicode(uuid.uuid4().hex))

        occ('app:enable user_ldap')

        # https://doc.owncloud.org/server/8.0/admin_manual/configuration_server/occ_command.html
        # This is a holdover from the early days, when there was no option to create additional configurations.
        # The second, and all subsequent, configurations that you create are automatically assigned IDs:
        occ('ldap:create-empty-config')
        occ('ldap:create-empty-config')

        occ('ldap:set-config s01 ldapHost ldap://localhost')
        occ('ldap:set-config s01 ldapPort 389')
        occ('ldap:set-config s01 ldapAgentName dc=syncloud,dc=org')
        occ('ldap:set-config s01 ldapBase dc=syncloud,dc=org')
        occ('ldap:set-config s01 ldapAgentPassword syncloud')

        occ('ldap:set-config s01 ldapLoginFilter "(&(|(objectclass=inetOrgPerson))(uid=%uid))"')

        occ('ldap:set-config s01 ldapUserFilterObjectclass inetOrgPerson')
        occ('ldap:set-config s01 ldapBaseUsers ou=users,dc=syncloud,dc=org')
        occ('ldap:set-config s01 ldapUserDisplayName cn')
        occ('ldap:set-config s01 ldapExpertUsernameAttr cn')

        occ('ldap:set-config s01 ldapGroupFilterObjectclass posixGroup')
        occ('ldap:set-config s01 ldapGroupDisplayName cn')
        occ('ldap:set-config s01 ldapBaseGroups ou=groups,dc=syncloud,dc=org')
        occ('ldap:set-config s01 ldapGroupFilter "(&(|(objectclass=posixGroup)))"')
        occ('ldap:set-config s01 ldapGroupMemberAssocAttr memberUid')

        occ('ldap:set-config s01 ldapTLS 0')
        occ('ldap:set-config s01 turnOffCertCheck 1')
        occ('ldap:set-config s01 ldapConfigurationActive 1')

        cron_cmd = config.cron_cmd()
        self.log.info("running: {0}".format(cron_cmd))
        self.log.info(check_output('sudo -H -u {0} {1}'.format(config.cron_user(), cron_cmd), shell=True))

        db_owncloud = Database(join(self.app.get_install_dir(), PSQL_PATH), database=DB_NAME, user=DB_USER)
        db_owncloud.execute("update oc_ldap_group_mapping set owncloud_name = 'admin';")
        db_owncloud.execute("update oc_ldap_group_members set owncloudname = 'admin';")

        occ('user:delete {0}'.format(INSTALL_USER))

    def prepare_storage(self):
        app_storage_dir = self.app.init_storage(USER_NAME)
        fs.touchfile(join(app_storage_dir, '.ocdata'))
        check_output('chmod 770 {0}'.format(app_storage_dir), shell=True)
        tmp_storage_path = join(app_storage_dir, 'tmp')
        fs.makepath(tmp_storage_path)
        fs.chownpath(tmp_storage_path, USER_NAME)

    def update_domain(self):
        app_domain = self.app.app_domain_name()
        local_ip = check_output(["hostname", "-I"]).split(" ")[0]
        domains = ['localhost', local_ip, app_domain]
        owncloud_config_set('trusted_domains', " ".join(domains))
