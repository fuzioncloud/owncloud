from ConfigParser import ConfigParser

default_config_file = '/opt/app/owncloud/config/owncloud-ctl.cfg'


class Config:

    def __init__(self, filename=default_config_file):
        self.parser = ConfigParser()
        self.parser.read(filename)
        self.filename = filename

    def port(self):
        return self.parser.getint('owncloud', 'port')

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