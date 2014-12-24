from setuptools import setup
from setuptools.command.install_scripts import install_scripts
from subprocess import check_output
from os.path import join, dirname

requirements = [
    'requests==2.2.1',
    'beautifulsoup4==4.3.2',
    'syncloud-app',
    'syncloud-insider'
]

class PostInstall(install_scripts):
    def run(self):
        install_scripts.run(self)
        print "installing ownCloud"
        print check_output("install-owncloud")

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-owncloud',
    description='ownCloud app',
    version=version,
    scripts=['bin/install-owncloud', 'bin/owncloud-ctl'],
    packages=['syncloud', 'syncloud.owncloud'],
    namespace_packages=['syncloud'],
    data_files=[('config', ['config/owncloud-ctl.cfg'])],
    install_requires=requirements,
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud',
    cmdclass={"install_scripts": PostInstall}
)
