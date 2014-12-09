from setuptools import setup
from setuptools.command.install_scripts import install_scripts
from subprocess import check_output


class PostInstall(install_scripts):
    def run(self):
        install_scripts.run(self)
        print "installing ownCloud"
        print check_output("install-owncloud")

setup(
    name='owncloud',
    version='7.0.1',
    scripts=['bin/install-owncloud'],
    description='ownCloud',
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@googlegroups.com',
    url='https://github.com/syncloud/owncloud',
    cmdclass={"install_scripts": PostInstall}
)
