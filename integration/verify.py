import json
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time
from subprocess import check_output

import pytest

from integration.util.loop import loop_device_add, loop_device_cleanup

app_path = join(dirname(__file__), '..')
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [abspath(join(lib_path, item)) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.insert(0, x), libs)

import requests
from bs4 import BeautifulSoup

device_user = 'user'
device_password = 'password'


@pytest.fixture(scope='function')
def syncloud_session():
    session = requests.session()
    session.post('http://localhost/server/rest/login', data={'name': device_user, 'password': device_password})
    return session


@pytest.fixture(scope='function')
def owncloud_session():
    session = requests.session()
    response = session.get('http://localhost/owncloud/', allow_redirects=False)
    soup = BeautifulSoup(response.text, "html.parser")
    requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
    response = session.post('http://localhost/owncloud/index.php',
                            data={'user': device_user, 'password': device_password, 'requesttoken': requesttoken},
                            allow_redirects=False)
    assert response.status_code == 302, response.text
    return session, requesttoken


def test_activate_device(auth):
    email, password, domain, release, version, arch = auth
    response = requests.post('http://localhost:81/server/rest/activate',
                             data={'redirect-email': email, 'redirect-password': password, 'redirect-domain': domain,
                                   'name': device_user, 'password': device_password,
                                   'api-url': 'http://api.syncloud.info:81', 'domain': 'syncloud.info',
                                   'release': release})
    assert response.status_code == 200


def test_install(auth):
    __local_install(auth)


def test_resource(owncloud_session):
    session, _ = owncloud_session
    assert session.get('http://localhost/owncloud/core/img/filetypes/text.png').status_code == 200


def test_visible_through_platform():
    response = requests.get('http://localhost/owncloud/', allow_redirects=False)
    assert response.status_code == 200, response.text


def test_admin(owncloud_session):
    session, _ = owncloud_session
    response = session.get('http://localhost/owncloud/index.php/settings/admin', allow_redirects=False)
    assert response.status_code == 200, response.text


def test_disk(syncloud_session, owncloud_session):

    loop_device_cleanup(0)
    loop_device_cleanup(1)

    device0 = loop_device_add('ext4', 0)
    __activate_disk(syncloud_session, device0)
    __create_test_dir(owncloud_session, 'test0')
    __check_test_dir(owncloud_session, 'test0')

    device1 = loop_device_add('ntfs', 1)
    __activate_disk(syncloud_session, device1)
    __create_test_dir(owncloud_session, 'test1')
    __check_test_dir(owncloud_session, 'test1')

    __activate_disk(syncloud_session, device0)
    __check_test_dir(owncloud_session, 'test0')

    loop_device_cleanup(0)
    loop_device_cleanup(1)


def __activate_disk(syncloud_session, loop_device):
    response = syncloud_session.get('http://localhost/server/rest/settings/disk_activate',
                                    params={'device': loop_device}, allow_redirects=False)
    assert response.status_code == 200, response.text


def __create_test_dir(owncloud_session, test_dir):
    owncloud_session, requesttoken = owncloud_session
    response = owncloud_session.post('http://localhost/owncloud/index.php/apps/files/ajax/newfolder.php',
                                     data={'dir': '', 'foldername': test_dir, 'requesttoken': requesttoken},
                                     allow_redirects=False)
    assert response.status_code == 200, response.text


def __check_test_dir(owncloud_session, test_dir):

    response = requests.get('http://localhost/owncloud')
    assert response.status_code == 200, BeautifulSoup(response.text, "html.parser").find('li', class_='error')

    owncloud_session, _ = owncloud_session
    response = owncloud_session.get('http://localhost/owncloud/index.php/apps/files/ajax/list.php?dir=/',
                                    allow_redirects=False)
    info = json.loads(response.text)
    dirs = map(lambda v: v['name'], info['data']['files'])
    assert test_dir in dirs, response.text


def test_remove(syncloud_session):
    response = syncloud_session.get('http://localhost/server/rest/remove?app_id=owncloud', allow_redirects=False)
    assert response.status_code == 200, response.text


def test_reinstall(auth):
    __local_install(auth)


def __local_install(auth):
    email, password, domain, release, version, arch = auth
    ssh = 'sshpass -p syncloud ssh -o StrictHostKeyChecking=no -p 2222 root@localhost'
    print(check_output('{0} /opt/app/sam/bin/sam --debug install /owncloud-{1}-{2}.tar.gz'.format(ssh, version, arch),
                       shell=True))
    time.sleep(3)
