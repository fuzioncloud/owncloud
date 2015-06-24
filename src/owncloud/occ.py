from subprocess import check_output
from owncloud.config import Config
from syncloud.app import logger


def occ(args):
    log = logger.get_logger('owncloud.occ')
    config = Config()
    output = check_output('{0}/occ-runner {1}'.format(config.bin_dir(), args), shell=True).strip()
    if output:
        log.info(output)
