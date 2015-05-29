from setuptools import setup
from os.path import join, dirname

requirements = [
    'requests',
    'beautifulsoup4',
    'syncloud-platform',
    'MySQL-python==1.2.5'
]

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-owncloud',
    description='ownCloud app',
    version=version,
    scripts=[
        'bin/syncloud-owncloud-post-install',
        'bin/syncloud-owncloud-post-upgrade',
        'bin/syncloud-owncloud-pre-remove',
        'bin/syncloud-owncloud-reconfigure',
        'bin/owncloud-ctl'],
    packages=['syncloud', 'syncloud.owncloud'],
    namespace_packages=['syncloud'],
    data_files=[
        ('syncloud-owncloud/config', ['config/owncloud-ctl.cfg']),
        ('syncloud-owncloud/config', ['config/owncloud.conf'])
    ],
    install_requires=requirements,
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud'
)