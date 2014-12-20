from setuptools import setup
from setuptools.command.install_scripts import install_scripts
from subprocess import check_output
from os.path import join, dirname

class PostInstall(install_scripts):
    def run(self):
        install_scripts.run(self)
        print "installing ownCloud"
        print check_output("install-owncloud")

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='owncloud',
    version=version,
    scripts=['bin/install-owncloud'],
    description='ownCloud',
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud',
    cmdclass={"install_scripts": PostInstall}
)
