import logging
from os.path import dirname
import pytest
import requests

from syncloud.app import logger
from syncloud.insider.facade import get_insider
from syncloud.sam.manager import get_sam
from syncloud.sam.pip import Pip
from syncloud.sam.platform_installer import PlatformInstaller
from syncloud.server.serverfacade import get_server

from syncloud.owncloud.installer import OwncloudInstaller
from syncloud.owncloud.setup import Setup

DIR = dirname(__file__)

@pytest.fixture(scope="session", autouse=True)
def activate_device(auth):

    logger.init(logging.DEBUG, True)

    print("installing latest platform")
    get_sam().update("0.9")
    get_sam().install("syncloud-platform")
    # PlatformInstaller().install()
    Pip(None).log_version('syncloud-platform')

    # persist upnp mock setting
    get_insider().insider_config.set_upnpc_mock(True)

    server = get_server(insider=get_insider(use_upnpc_mock=True))
    email, password = auth
    server.activate('test', 'syncloud.info', 'http://api.syncloud.info:81', email, password, 'teamcity', 'user', 'password', False)


def test_owncloud_activation():
    logger.init(logging.DEBUG, True)

    print("installing local owncloud build")
    OwncloudInstaller().install('owncloud.tar.gz')

    setup = Setup()
    assert not setup.is_finished()
    setup.finish('test', 'test')
    assert setup.is_finished()

def test_platform_integration():
    session = requests.session()
    response = session.get('http://localhost/owncloud', allow_redirects=False)
    # print(response.text.encode('ascii', 'ignore'))
    assert response.status_code == 200

    response = session.post('http://localhost/owncloud', data={'name': 'user', 'password': 'password'})
    # print(response.text)
    assert session.get('http://localhost/owncloud', allow_redirects=False).status_code == 200
