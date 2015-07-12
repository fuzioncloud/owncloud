from subprocess import check_output
from syncloud_app import logger

from owncloud.config import Config

def occ(args):
    log = logger.get_logger('owncloud.occ')
    config = Config()
    output = check_output('{0}/occ-runner {1}'.format(config.bin_dir(), args), shell=True).strip()
    if output:
        log.info(output)
