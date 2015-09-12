from os import environ, symlink
import os
from os.path import isdir, join, isfile
import shutil
import uuid
import massedit
import pwd
from subprocess import check_output

from syncloud_app import logger
from syncloud_platform.systemd.systemctl import remove_service, add_service
from syncloud_platform.tools import app
from syncloud_platform.tools.nginx import Nginx

from owncloud import postgres
from owncloud.config import Config
from owncloud.cron import OwncloudCron
from owncloud.occ import occ
from owncloud.webface import Setup

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'
SYSTEMD_POSTGRESQL = 'owncloud-postgresql'
INSTALL_USER = 'installer'


class OwncloudInstaller:
    def __init__(self):
        self.log = logger.get_logger('owncloud.installer')

    def install(self):

        config = Config()

        if 'LANG' in environ:
            lang = environ['LANG']
            if lang not in check_output(['locale', '-a']):
                print("generating locale: {0}".format(lang))
                fix_locale_gen(lang)
                check_output('locale-gen')

        try:
            pwd.getpwnam(config.cron_user())
        except KeyError:
            self.log.info(check_output('/usr/sbin/useradd -r -s /bin/false {0}'.format(config.cron_user()), shell=True))
        self.log.info(check_output('chown -R {0}. {1}'.format(config.cron_user(), config.install_path()), shell=True))

        app_data_dir = app.get_app_data_root('owncloud', config.cron_user())
        if not isdir(join(app_data_dir, 'config')):
            app.create_data_dir(app_data_dir, 'config', config.cron_user())

        symlink(join(app_data_dir, 'config'), config.owncloud_config_link())
        app.create_data_dir(app_data_dir, 'data', 'owncloud')

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)
        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

        if not self.installed():
            self.initialize(config)

        Nginx().add_app('owncloud', config.port())

        cron = OwncloudCron(config)
        cron.remove()
        cron.create()

        ca_bundle_file = 'ca-bundle.crt'
        from_ca_bundle_certificate = '{0}/{1}'.format(config.original_config_dir(), ca_bundle_file)
        to_ca_bundle_certificate = '{0}/{1}'.format(config.config_path, ca_bundle_file)
        if isfile(to_ca_bundle_certificate):
            os.remove(to_ca_bundle_certificate)
        shutil.copyfile(from_ca_bundle_certificate, to_ca_bundle_certificate)

    def remove(self):

        config = Config()
        Nginx().remove_app('owncloud')
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
            self.log.info(check_output(cron_cmd, shell=True))

            postgres.execute("update oc_ldap_group_mapping set owncloud_name = 'admin';")
            postgres.execute("update oc_ldap_group_members set owncloudname = 'admin';")

            occ('user:delete {0}'.format(INSTALL_USER))


def fix_locale_gen(lang, locale_gen='/etc/locale.gen'):
    editor = massedit.MassEdit()
    editor.append_code_expr("re.sub('# {0}', '{0}', line)".format(lang))
    editor.edit_file(locale_gen)
