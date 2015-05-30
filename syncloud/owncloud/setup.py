import requests
import re
from bs4 import BeautifulSoup
import logging
from syncloud.app import logger

def finish(owncloud_url, login, password):
    log = logger.get_logger('owncloud.setup.finish')

    if is_finished(owncloud_url):
        return True

    index_url = get_index_url(owncloud_url)

    log.info("will finish setup using: {0}".format(index_url))

    response = requests.post(index_url,
                             data={
                                 'install': 'true', 'adminlogin': login,
                                 'adminpass': password, 'adminpass-clone': password,
                                 'dbtype': 'mysql', 'dbname': 'owncloud',
                                 'dbuser': 'root', 'dbpass': 'root',
                                 'dbhost': 'localhost', 'directory': '/data'}, allow_redirects=False)
    if response.status_code != 200:
        raise Exception("unable to finish setup: {}".format(response.text))

    soup = BeautifulSoup(response.text)
    errors = soup.find('fieldset', class_='warning')
    if errors:
        errors = re.sub('(\n|\t)', '', errors.text)
        errors = re.sub('( +)', ' ', errors)
        raise Exception(errors)


def is_finished(owncloud_url):
    log = logger.get_logger('owncloud.setup.is_finished')
    index_url = get_index_url(owncloud_url)
    try:
        response = requests.get(index_url, verify=False)
        log.debug('{0} response'.format(index_url))
        log.debug(response)
        if response.status_code == 400:
            raise Exception("ownCloud is not trusting you to access {}".format(index_url))

        if response.status_code != 200:
            soup = BeautifulSoup(response.text)
            error = soup.find('li', class_='error')
            log.error(error)
            raise Exception("ownCloud is not available at {}".format(index_url))

        return "Finish setup" not in response.text

    except requests.ConnectionError:
        raise Exception("ownCloud is not available at {}".format(index_url))


def get_index_url(owncloud_url):
    return '{}/index.php'.format(owncloud_url)



