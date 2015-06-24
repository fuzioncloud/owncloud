import os
import shutil
from subprocess import check_output
import uuid
from syncloud.app import logger
from syncloud.systemd.systemctl import remove_service, add_service
from syncloud.tools import app
from syncloud.tools.nginx import Nginx
from os.path import isdir, join
import massedit
import pwd
from owncloud import postgres
from owncloud.config import Config
from owncloud.cron import OwncloudCron
from owncloud.occ import occ
from owncloud.setup import Setup

SYSTEMD_NGINX_NAME = 'owncloud-nginx'
SYSTEMD_PHP_FPM_NAME = 'owncloud-php-fpm'
SYSTEMD_POSTGRESQL = 'owncloud-postgresql'
INSTALL_USER = 'installer'


class OwncloudInstaller:
    def __init__(self):
        self.log = logger.get_logger('owncloud.installer')

    def install(self):

        config = Config()

        if 'LANG' in os.environ:
            lang = os.environ['LANG']
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

        os.symlink(join(app_data_dir, 'config'), config.owncloud_config_link())
        app.create_data_dir(app_data_dir, 'data', 'owncloud')

        print("setup systemd")
        add_service(config.install_path(), SYSTEMD_POSTGRESQL)

        postgres.execute("ALTER USER owncloud WITH PASSWORD 'owncloud';", database="postgres")

        add_service(config.install_path(), SYSTEMD_PHP_FPM_NAME)
        add_service(config.install_path(), SYSTEMD_NGINX_NAME)

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

        Nginx().add_app('owncloud', config.port())

        OwncloudCron(config).create()

    def remove(self):

        config = Config()
        Nginx().remove_app('owncloud')
        cron = OwncloudCron(config)
        remove_service(SYSTEMD_NGINX_NAME)
        remove_service(SYSTEMD_PHP_FPM_NAME)
        remove_service(SYSTEMD_POSTGRESQL)

        cron.remove()

        if os.path.isdir(config.install_path()):
            shutil.rmtree(config.install_path())

def fix_locale_gen(lang, locale_gen='/etc/locale.gen'):
    massedit.edit_files([locale_gen], ["re.sub('# {0}', '{0}', line)".format(lang)], dry_run=False)
