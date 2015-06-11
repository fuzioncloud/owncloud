from bs4 import BeautifulSoup
import logging
from os.path import dirname

import pytest
import requests

from syncloud.app import logger
from syncloud.owncloud.installer import OwncloudInstaller
from syncloud.owncloud.setup import Setup

DIR = dirname(__file__)

@pytest.fixture(scope="session", autouse=True)
def activate_device(auth):

    logger.init(logging.DEBUG, True)

    email, password = auth

    response = requests.post('http://localhost:81/server/rest/activate',
                             data={'redirect-email': email, 'redirect-password': password,
                                   'redirect-domain': 'teamcity', 'name': 'user', 'password': 'password',
                                   'api-url': 'http://api.syncloud.info:81', 'domain': 'syncloud.info'})
    assert response.status_code == 200


def test_owncloud_activation():
    logger.init(logging.DEBUG, True)

    setup = Setup()
    assert not setup.is_finished()
    setup.finish('test', 'test', overwritehost='localhost')
    assert setup.is_finished()

def test_platform_integration():
    session = requests.session()
    response = session.get('http://localhost/owncloud', allow_redirects=False)
    # print(response.text)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text)
    requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
    response = session.post('http://localhost/owncloud/index.php',
                            data={'user': 'test', 'password': 'test', 'requesttoken': requesttoken},
                            allow_redirects=False)
    assert response.status_code == 302
    # print(response.text)
    # assert session.get('http://localhost/owncloud', allow_redirects=False).status_code == 302

    assert session.get('http://localhost/owncloud/core/img/filetypes/text.png').status_code == 200
