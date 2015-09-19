from subprocess import check_output
from owncloud.config import Config


def owncloud_config_set(key, value):
    config = Config()
    print(check_output('{0}/owncloud-config {1} {2}'.format(
        config.bin_dir(),
        key,
        "'{0}'".format(value)), shell=True).strip())
