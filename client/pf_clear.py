import datetime
import time
import signal
import sys

from logger.logger_clear import logger_clear

from database.db import Database
from database.postgres import connect, disconnect


def signal_handler(sig, frame):
    logger_clear.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db = Database(conn)

try:
    while True:
        start_time = time.time()

        current_datetime = datetime.datetime.now()
        one_day_ago_datetime = current_datetime - datetime.timedelta(days=1)
        one_day_ago_timestamp = int(one_day_ago_datetime.timestamp())
        logger_clear.info("Время ровно сутки назад - int: %s", one_day_ago_timestamp)

        deleted_rows = db.pf_delete_params_by_time(one_day_ago_timestamp)
        delete_time = time.time()
        count_all_rows = db.pf_select_count_all()

        clear_time = time.time()
        logger_clear.info(f"DB(pf): Удалено строк: {deleted_rows}, Осталось строк: {count_all_rows}, \n"
                          f"Затраченное время: {clear_time - start_time}: удаление - {delete_time - start_time} подсчет - {clear_time - delete_time}")

        time.sleep(3600)

except Exception as e:
    logger_clear.error("Произошла ошибка: %s", e)
    disconnect(conn)
    sys.exit(1)