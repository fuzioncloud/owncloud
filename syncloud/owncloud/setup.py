import requests
import re
from bs4 import BeautifulSoup
import logging

log = logging.getLogger()


def finish(owncloud_url, login, password):

    if is_finished(owncloud_url):
        return True

    index_url = get_index_url(owncloud_url)

    log.debug("will finish setup using: %s", index_url)

    response = requests.post(index_url,
                             data={
                                 'install': 'true', 'adminlogin': login,
                                 'adminpass': password, 'adminpass-clone': password,
                                 'dbtype': 'mysql', 'dbname': 'owncloud',
                                 'dbuser': 'root', 'dbpass': 'root',
                                 'dbhost': 'localhost', 'directory': '/data'})
    if response.status_code != 200:
        raise Exception("unable to finish setup: {}".format(response.text))

    soup = BeautifulSoup(response.text)
    errors = soup.find('fieldset', class_='warning')
    if errors:
        errors = re.sub('(\n|\t)', '', errors.text)
        errors = re.sub('( +)', ' ', errors)
        raise Exception(errors)


def is_finished(owncloud_url):
    index_url = get_index_url(owncloud_url)
    try:
        response = requests.get(index_url, verify=False)
        if response.status_code == 400:
            raise Exception("ownCloud is not trusting you to access {}".format(index_url))

        if response.status_code != 200:
            raise Exception("ownCloud is not available at {}".format(index_url))

        return "Finish setup" not in response.text

    except requests.ConnectionError:
        raise Exception("ownCloud is not available at {}".format(index_url))


def get_index_url(owncloud_url):
    return '{}/index.php'.format(owncloud_url)


