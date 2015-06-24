from setuptools import setup
from os.path import join, dirname

requirements = [
    'requests',
    'beautifulsoup4',
    'massedit==0.66',
]

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-owncloud',
    description='ownCloud app',
    version=version,
    packages=['owncloud'],
    install_requires=requirements,
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud'
)