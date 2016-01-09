import json
import os
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time
from subprocess import check_output

import pytest
import shutil

from integration.util.loop import loop_device_add, loop_device_cleanup
from integration.util.ssh import run_scp, ssh_command, SSH, run_ssh, set_docker_ssh_port

app_path = join(dirname(__file__), '..')
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [abspath(join(lib_path, item)) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.append(x), libs)

import requests
from bs4 import BeautifulSoup

SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
OWNCLOUD_URL = 'localhost:1082'
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')


@pytest.fixture(scope='module')
def user_domain(auth):
    email, password, domain, release, version, arch = auth
    return 'owncloud.{0}.{1}'.format(domain, SYNCLOUD_INFO)


@pytest.fixture(scope='function')
def syncloud_session():
    session = requests.session()
    session.post('http://localhost/server/rest/login', data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


@pytest.fixture(scope='function')
def owncloud_session_domain(user_domain):
    session = requests.session()
    response = session.get('http://127.0.0.1', headers={"Host": user_domain}, allow_redirects=False)
    # print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
    response = session.post('http://127.0.0.1/index.php',
                            headers={"Host": user_domain},
                            data={'user': DEVICE_USER, 'password': DEVICE_PASSWORD, 'requesttoken': requesttoken},
                            allow_redirects=False)
    assert response.status_code == 302, response.text
    return session, requesttoken


def test_remove_logs():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def test_activate_device(auth):
    email, password, domain, release, version, arch = auth
    response = requests.post('http://localhost:81/server/rest/activate',
                             data={'redirect-email': email, 'redirect-password': password, 'redirect-domain': domain,
                                   'name': DEVICE_USER, 'password': DEVICE_PASSWORD,
                                   'api-url': 'http://api.{0}'.format(SYNCLOUD_INFO), 'domain': SYNCLOUD_INFO,
                                   'release': release})
    assert response.status_code == 200, response.text


def test_enable_external_access(syncloud_session):
    response = syncloud_session.get('http://localhost/server/rest/settings/set_protocol', params={'protocol': 'https'})
    assert '"success": true' in response.text
    assert response.status_code == 200


def test_install(auth):
    __local_install(auth)


def test_resource(owncloud_session_domain, user_domain):
    session, _ = owncloud_session_domain
    response = session.get('http://127.0.0.1/core/img/filetypes/text.png', headers={"Host": user_domain})
    assert response.status_code == 200, response.text


def test_visible_through_platform(auth, user_domain):
    response = requests.get('http://127.0.0.1', headers={"Host": user_domain}, allow_redirects=False)
    assert response.status_code == 200, response.text


def test_admin(owncloud_session_domain, user_domain):
    session, _ = owncloud_session_domain
    response = session.get('http://127.0.0.1/index.php/settings/admin', headers={"Host": user_domain}, allow_redirects=False)
    assert response.status_code == 200, response.text


def test_disk(syncloud_session, owncloud_session_domain, user_domain):

    loop_device_cleanup(0, DEVICE_PASSWORD)
    loop_device_cleanup(1, DEVICE_PASSWORD)

    device0 = loop_device_add('ext4', 0, DEVICE_PASSWORD)
    __activate_disk(syncloud_session, device0)
    __create_test_dir(owncloud_session_domain, 'test0', user_domain)
    __check_test_dir(owncloud_session_domain, 'test0', user_domain)

    device1 = loop_device_add('ntfs', 1, DEVICE_PASSWORD)
    __activate_disk(syncloud_session, device1)
    __create_test_dir(owncloud_session_domain, 'test1', user_domain)
    __check_test_dir(owncloud_session_domain, 'test1', user_domain)

    __activate_disk(syncloud_session, device0)
    __check_test_dir(owncloud_session_domain, 'test0', user_domain)

    loop_device_cleanup(0, DEVICE_PASSWORD)
    loop_device_cleanup(1, DEVICE_PASSWORD)


def __activate_disk(syncloud_session, loop_device):
    response = syncloud_session.get('http://localhost/server/rest/settings/disk_activate',
                                    params={'device': loop_device}, allow_redirects=False)
    assert response.status_code == 200, response.text


def __create_test_dir(owncloud_session, test_dir, user_domain):
    owncloud_session, requesttoken = owncloud_session
    response = owncloud_session.post('http://127.0.0.1/index.php/apps/files/ajax/newfolder.php',
                                     headers={"Host": user_domain},
                                     data={'dir': '', 'foldername': test_dir, 'requesttoken': requesttoken},
                                     allow_redirects=False)
    assert response.status_code == 200, response.text


def __check_test_dir(owncloud_session, test_dir, user_domain):

    response = requests.get('http://127.0.0.1', headers={"Host": user_domain})
    assert response.status_code == 200, BeautifulSoup(response.text, "html.parser").find('li', class_='error')

    owncloud_session, _ = owncloud_session
    response = owncloud_session.get('http://127.0.0.1/index.php/apps/files/ajax/list.php?dir=/',
                                    headers={"Host": user_domain},
                                    allow_redirects=False)
    info = json.loads(response.text)
    dirs = map(lambda v: v['name'], info['data']['files'])
    assert test_dir in dirs, response.text


def test_remove(syncloud_session):
    response = syncloud_session.get('http://localhost/server/rest/remove?app_id=owncloud', allow_redirects=False)
    assert response.status_code == 200, response.text


def test_reinstall(auth):
    __local_install(auth)


def test_copy_logs():
    os.mkdir(LOG_DIR)
    run_scp('root@localhost:/opt/data/platform/log/* {0}'.format(LOG_DIR), password=DEVICE_PASSWORD)

    print('-------------------------------------------------------')
    print('syncloud docker image is running')
    print('connect using: {0}'.format(ssh_command(DEVICE_PASSWORD, SSH)))
    print('-------------------------------------------------------')


def __local_install(auth):
    email, password, domain, release, version, arch = auth
    run_scp('{0}/../owncloud-{1}-{2}.tar.gz root@localhost:/'.format(DIR, version, arch), password=DEVICE_PASSWORD)
    run_ssh('/opt/app/sam/bin/sam --debug install /owncloud-{0}-{1}.tar.gz'.format(version, arch), password=DEVICE_PASSWORD)
    set_docker_ssh_port(DEVICE_PASSWORD)
    time.sleep(3)