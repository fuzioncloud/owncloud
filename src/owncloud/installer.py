from os import environ, symlink
import os
from os.path import isdir, join, isfile
import shutil
from sys import path
import uuid
from subprocess import check_output

from syncloud_app import logger
from syncloud_platform.systemd.systemctl import remove_service, add_service
from syncloud_platform.tools import app
from syncloud_platform.tools.nginx import Nginx
from syncloud_platform.tools.touch import touch
from syncloud_platform.api import storage, info
from syncloud_platform.tools import chown, locale

from owncloud import postgres
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


class OwncloudInstaller:
    def __init__(self):
        self.log = logger.get_logger('owncloud.installer')

    def install(self):

        config = Config()

        locale.fix_locale()

        chown.chown(APP_NAME, config.install_path())

        app_data_dir = app.get_app_data_root(APP_NAME, config.cron_user())

        if not isdir(join(app_data_dir, 'config')):
            app.create_data_dir(app_data_dir, 'config', config.cron_user())

        symlink(join(app_data_dir, 'config'), config.owncloud_config_link())
        app.create_data_dir(app_data_dir, 'data', APP_NAME)

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)
        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

        self.prepare_storage()

        if not self.installed():
            self.initialize(config)

        Nginx().add_app(APP_NAME, config.port())

        cron = OwncloudCron(config)
        cron.remove()
        cron.create()

        owncloud_config_set('memcache.local', '\OC\Memcache\APCu')
        owncloud_config_set('loglevel', '2')
        owncloud_config_set('logfile', config.log_file())

        self.update_domain()

    def remove(self):

        config = Config()
        Nginx().remove_app(APP_NAME)
        cron = OwncloudCron(config)
        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)
        remove_service(SYSTEMD_POSTGRESQL)

        cron.remove()

        if isdir(config.install_path()):
            shutil.rmtree(config.install_path())

    def installed(self):
        config = Config()
        if not isfile(config.config_file()):
            return False

        return 'installed' in open(config.config_file()).read().strip()

    def initialize(self, config):

            print("initialization")
            postgres.execute("ALTER USER owncloud WITH PASSWORD 'owncloud';", database="postgres")

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

            postgres.execute("update oc_ldap_group_mapping set owncloud_name = 'admin';")
            postgres.execute("update oc_ldap_group_members set owncloudname = 'admin';")

            occ('user:delete {0}'.format(INSTALL_USER))

    def prepare_storage(self):
        app_storage_dir = storage.init(APP_NAME, APP_NAME)
        touch(join(app_storage_dir, '.ocdata'))

    def update_domain(self):
        domain = info.domain()
        local_ip = check_output(["hostname", "-I"]).split(" ")[0]
        domains = ['localhost', local_ip ,domain]
        owncloud_config_set('trusted_domains', " ".join(domains))
