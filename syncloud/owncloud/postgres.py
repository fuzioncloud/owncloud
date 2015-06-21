import psycopg2
from syncloud.app import logger

USER = "owncloud"
DATABASE = "owncloud"


def execute(sql, database=DATABASE):
    log = logger.get_logger('owncloud.postgres.execute')

    conn = psycopg2.connect(database=database, user=USER, host="/tmp")
    with conn:
        with conn.cursor() as curs:
            log.info("executing: {0}".format(sql))
            curs.execute(sql)

def select(sql, database=DATABASE):
    log = logger.get_logger('owncloud.postgres.select')

    conn = psycopg2.connect(database=database, user=USER, host="/tmp")
    with conn:
        with conn.cursor() as curs:
            log.info("executing: {0}".format(sql))
            curs.execute(sql)
            return [record for record in curs]