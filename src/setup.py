from setuptools import setup
from os.path import join, dirname

requirements = [
    'requests',
    'beautifulsoup4',
    'syncloud-platform',
    'psycopg2==2.6',
    'massedit==0.66',
]

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-owncloud',
    description='ownCloud app',
    version=version,
    scripts=[
        'bin/syncloud-owncloud-post-install',
        'bin/syncloud-owncloud-pre-remove',
        'bin/syncloud-owncloud-reconfigure',
        'bin/owncloud-ctl'],
    packages=['syncloud', 'syncloud.owncloud'],
    namespace_packages=['syncloud'],
    install_requires=requirements,
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud'
)