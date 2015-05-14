from ConfigParser import ConfigParser
from os.path import join
from syncloud.tools.facade import Facade

tools_facade = Facade()
default_config_path = join(tools_facade.usr_local_dir(), 'syncloud-owncloud', 'config', 'owncloud-ctl.cfg')


class Config:

    def __init__(self, filename=default_config_path):
        self.parser = ConfigParser()
        self.parser.read(filename)
        self.filename = filename

    def service_name(self):
        return self.parser.get('owncloud', 'service_name')

    def port_http(self):
        return self.parser.getint('owncloud', 'port_http')

    def service_type_http(self):
        return self.parser.get('owncloud', 'service_type_http')

    def port_https(self):
        return self.parser.getint('owncloud', 'port_https')

    def service_type_https(self):
        return self.parser.get('owncloud', 'service_type_https')

    def url(self):
        return self.parser.get('owncloud', 'url')

    def config_file(self):
        return self.parser.get('owncloud', 'config_file')

    def site_config_file(self):
        return self.parser.get('owncloud', 'site_config_file')

    def site_name(self):
        return self.parser.get('owncloud', 'site_name')

    def install_path(self):
        return self.parser.get('owncloud', 'install_path')

    def cron_user(self):
        return self.parser.get('owncloud', 'cron_user')

    def cron_cmd(self):
        return self.parser.get('owncloud', 'cron_cmd')

    def apache_link(self):
        return self.parser.get('owncloud', 'apache_link')

    def data_dir(self):
        return self.parser.get('owncloud', 'data_dir')