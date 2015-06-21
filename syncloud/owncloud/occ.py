from subprocess import check_output
from syncloud.owncloud.config import Config


def occ(args):
    config = Config()
    check_output('{0}/occ-runner {1}'.format(config.bin_dir(), args), shell=True)
