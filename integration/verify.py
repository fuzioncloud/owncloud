from bs4 import BeautifulSoup
import logging
from os.path import dirname, join, abspath

import requests
import time
from subprocess import check_output
from syncloud_app import logger

DIR = dirname(__file__)
APP_DIR = abspath(join(DIR, '..'))

device_user = 'user'
device_password = 'password'

def test_activate_device(auth):
    email, password, domain, release, version, arch = auth
    response = requests.post('http://localhost:81/server/rest/activate',
                             data={'redirect-email': email, 'redirect-password': password, 'redirect-domain': domain,
                                   'name': device_user, 'password': device_password,
                                   'api-url': 'http://api.syncloud.info:81', 'domain': 'syncloud.info',
                                   'release': release})
    assert response.status_code == 200

def test_owncloud_install(auth):
    email, password, domain, release, version, arch = auth
    logger.init(logging.DEBUG, True)
    log = logger.get_logger('test_owncloud_install')
    log.info(check_output('/opt/app/sam/bin/sam --debug install /test/owncloud-{0}-{1}.tar.gz'.format(version, arch), shell=True))
    time.sleep(3)

def test_visible_through_platform():
    session = requests.session()
    response = session.get('http://localhost/owncloud/', allow_redirects=False)
    assert response.status_code == 200

def test_login():
    session = requests.session()
    response = session.get('http://localhost/owncloud/', allow_redirects=False)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text)
    requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
    response = session.post('http://localhost/owncloud/index.php',
                            data={'user': device_user, 'password': device_password, 'requesttoken': requesttoken},
                            allow_redirects=False)
    assert response.status_code == 302

    assert session.get('http://localhost/owncloud/core/img/filetypes/text.png').status_code == 200
