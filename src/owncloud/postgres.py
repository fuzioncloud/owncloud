from syncloud_app import logger
from subprocess import check_output

from owncloud.config import Config

USER = "owncloud"
DATABASE = "owncloud"


def execute(sql, database=DATABASE):
    log = logger.get_logger('owncloud.postgres.execute')
    config = Config()
    log.info("executing: {0}".format(sql))
    log.info(check_output('{0} -U {1} -d {2} -c "{3}"'.format(config.psql(), USER, database, sql), shell=True))
