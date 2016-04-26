from subprocess import check_output
from syncloud_app import logger

from owncloud.config import Config


def occ(args):
    log = logger.get_logger('owncloud.occ')
    config = Config()
    output = check_output('{0}/occ-runner {1}'.format(config.bin_dir(), args), shell=True).strip()
    if output:
        log.info(output)


def owncloud_config_set(key, value):
    config = Config()
    print(check_output('{0}/owncloud-config {1} {2}'.format(
        config.bin_dir(),
        key,
        "'{0}'".format(value)), shell=True).strip())
