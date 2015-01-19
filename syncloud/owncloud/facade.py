import os
from ConfigParser import ConfigParser
from os.path import join
from syncloud.apache.facade import AoacheFacade
from syncloud.tools.facade import Facade

from config import Config
from configmanager import ConfigManager
from access import Access
import setup


tools_facade = Facade()
default_config_path = join(tools_facade.usr_local_dir(), 'syncloud-owncloud', 'config')


class OwncloudControl:
    def __init__(self, config, insider, access, config_manager):
        self.config_manager = config_manager
        self.config = config
        self.insider = insider
        self.access = access

    def finish(self, login, password, host, protocol):
        owncloud_url = 'http://{}:{}/{}'.format(host, self.config.port_http, self.config.url)
        setup.finish(owncloud_url, login, password)
        protocol = protocol.lower()
        if protocol == 'https':
            self.access.https_on()
        elif protocol == 'http':
            self.access.https_off()
        else:
            raise Exception('Unknown protocol {}, it should either http or https'.format(protocol))
        self.config_manager.overwrite_webroot()

    def https_on(self):
        return self.access.https_on()

    def https_off(self):
        return self.access.https_off()

    def _get_url(self, info):
        url = '{0}://{1}:{2}'.format(info.service.protocol, info.external_host, info.external_port)
        if info.service.url:
            url += '/'+info.service.url
        return url

    def url(self):
        info = self.insider.service_info(self.config.service_name)
        return self._get_url(info)

    def verify(self, host):
        owncloud_url = 'http://{}:{}/{}'.format(host, self.config.port_http, self.config.url)
        if not setup.is_finished(owncloud_url):
            raise Exception("not finished yet")
        else:
            return "finished"


def get_control(insider, config_path=default_config_path):
    config_filename = os.path.join(config_path, 'owncloud-ctl.cfg')

    parser = ConfigParser()
    parser.read(config_filename)

    service_name = parser.get('owncloud', 'service_name')
    port_http = parser.getint('owncloud', 'port_http')
    service_type_http = parser.get('owncloud', 'service_type_http')
    port_https = parser.getint('owncloud', 'port_https')
    service_type_https = parser.get('owncloud', 'service_type_https')
    url = parser.get('owncloud', 'url')
    config_file = parser.get('owncloud', 'config_file')
    site_config_file = parser.get('owncloud', 'site_config_file')
    site_name = parser.get('owncloud', 'site_name')

    config = Config(service_name, port_http, service_type_http, port_https, service_type_https, url, config_file,
                    site_config_file, site_name, config_path)

    config_manager = ConfigManager(config.config_file)
    access = Access(config, insider, config_manager, AoacheFacade())

    return OwncloudControl(config, insider, access, config_manager)