from ConfigParser import ConfigParser
from os.path import join

default_config_path = '/opt/app/owncloud/config'
default_config_file = join(default_config_path, 'owncloud-ctl.cfg')


class Config:

    def __init__(self, filename=default_config_file, config_path=default_config_path):
        self.parser = ConfigParser()
        self.parser.read(filename)
        self.filename = filename
        self.config_path = config_path

    def port(self):
        return self.parser.getint('owncloud', 'port')

    def url(self):
        return self.parser.get('owncloud', 'url')

    def config_file(self):
        return self.parser.get('owncloud', 'config_file')

    def data_dir(self):
        return self.parser.get('owncloud', 'data_dir')

    def app_data_dir(self):
        return self.parser.get('owncloud', 'app_data_dir')

    def log_dir(self):
        return self.parser.get('owncloud', 'log_dir')

    def log_file(self):
        return self.parser.get('owncloud', 'log_file')

    def root_path(self):
        return self.parser.get('owncloud', 'root_path')