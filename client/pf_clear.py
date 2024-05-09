import datetime
import time
import signal
import sys

from database.pf import Pf
from database.postgres import connect, disconnect
from logger.logger_clear import logger_clear


def signal_handler(sig, frame):
    logger_clear.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db = Pf(conn)

try:
    while True:
        current_datetime = datetime.datetime.now()
        one_day_ago_datetime = current_datetime - datetime.timedelta(days=1)
        one_day_ago_timestamp = int(one_day_ago_datetime.timestamp())
        logger_clear.info("Время ровно сутки назад - int: %s", one_day_ago_timestamp)

        deleted_rows = db.pf_delete_params(one_day_ago_timestamp)

        logger_clear.info("DB(pf): удалено строк: %s", deleted_rows)
        logger_clear.info("Стало строк: %s", db.pf_count_all())

        time.sleep(3600)

except Exception as e:
    logger_clear.error("Произошла ошибка: %s", e)
    disconnect(conn)
    sys.exit(1)