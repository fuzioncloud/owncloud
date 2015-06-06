from os.path import join
import requests
import re
from bs4 import BeautifulSoup
from subprocess import check_output
from syncloud.app import logger
from syncloud.insider.facade import get_insider
from syncloud.owncloud.config import Config


class Setup:
    def __init__(self):
        self.log = logger.get_logger('owncloud.setup.finish')
        self.config = Config()
        self.index_url = 'http://localhost:{}/index.php'.format(self.config.port())

    def finish(self, login, password, overwritehost=None):

        if self.is_finished():
            return True

        self.log.info("will finish setup using: {0}".format(self.index_url))

        response = requests.post(self.index_url,
                                 data={
                                     'install': 'true', 'adminlogin': login,
                                     'adminpass': password, 'adminpass-clone': password,
                                     'dbtype': 'pgsql', 'dbname': 'owncloud',
                                     'dbuser': 'owncloud', 'dbpass': 'owncloud',
                                     'dbhost': 'localhost', 'directory': self.config.data_dir()}, allow_redirects=False)

        if response.status_code == 302:
            self.log.info("successful login redirect")
            self.fix_owncloud_configuration(overwritehost)
            return True

        if response.status_code != 200:
            raise Exception("unable to finish setup: {0}: {0}".format(response.status_code, response.text))

        soup = BeautifulSoup(response.text)
        errors = soup.find('fieldset', class_='warning')
        if errors:
            errors = re.sub('(\n|\t)', '', errors.text)
            errors = re.sub('( +)', ' ', errors)
            raise Exception(errors)

    def fix_owncloud_configuration(self, overwritehost):
        owncloud_config_bin = join(self.config.bin_dir(), 'owncloud-config')
        if not overwritehost:
            info = get_insider().service_info('server')
            overwritehost = '{0}:{1}'.format(info.external_host, info.external_port)
        overwritewebroot = '/owncloud'
        self.log.info("running {0} {1} {2}".format(owncloud_config_bin, overwritehost, overwritewebroot))
        check_output([owncloud_config_bin, overwritehost, overwritewebroot])

    def is_finished(self,):

        try:
            response = requests.get(self.index_url, verify=False)
            self.log.debug('{0} response'.format(self.index_url))
            self.log.debug(response)
            if response.status_code == 400:
                raise Exception("ownCloud is not trusting you to access {}".format(self.index_url))

            if response.status_code != 200:
                soup = BeautifulSoup(response.text)
                error = soup.find('li', class_='error')
                self.log.error(error)
                raise Exception("ownCloud is not available at {}".format(self.index_url))

            return "Finish setup" not in response.text

        except requests.ConnectionError:
            raise Exception("ownCloud is not available at {}".format(self.index_url))
