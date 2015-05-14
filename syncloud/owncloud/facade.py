import os
from ConfigParser import ConfigParser
from os.path import join
from syncloud.apache.facade import ApacheFacade
from syncloud.tools.facade import Facade

from config import Config
from configmanager import ConfigManager
from access import Access
import setup


class OwncloudControl:
    def __init__(self, config, insider, access, config_manager):
        self.config_manager = config_manager
        self.config = config
        self.insider = insider
        self.access = access

    def finish(self, login, password, host, protocol):

        # Activation needs default http owncloud site
        self.access.enable_http_web()

        owncloud_url = 'http://{}:{}/{}'.format(host, self.config.port_http(), self.config.url())
        setup.finish(owncloud_url, login, password)

        # Now we can switch to
        self.access.mode(protocol.lower())

    def https_on(self):
        self.access.mode('https')

    def https_off(self):
        self.access.mode('http')

    def _get_url(self, info):
        url = '{0}://{1}:{2}'.format(info.service.protocol, info.external_host, info.external_port)
        if info.service.url:
            url += '/'+info.service.url
        return url

    def url(self):
        info = self.insider.service_info(self.config.service_name())
        return self._get_url(info)

    def verify(self, host):
        owncloud_url = 'http://{}:{}/{}'.format(host, self.config.port_http(), self.config.url())
        if not setup.is_finished(owncloud_url):
            raise Exception("not finished yet")
        else:
            return "finished"

    def reconfigure(self):
        self.access.update_trusted_info()


def get_control(insider):

    config = Config()

    config_manager = ConfigManager(config.config_file())
    access = Access(config, insider, config_manager, ApacheFacade())

    return OwncloudControl(config, insider, access, config_manager)