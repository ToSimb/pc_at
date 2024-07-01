import requests
import time
import signal
import sys

from database.db import Database
from database.postgres import connect, disconnect
from logger.logger_check import logger_check

from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, T3, DEBUG

def signal_handler(sig, frame):
    logger_check.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db = Database(conn)


def request_conn(vvk_id: int, user_query_interval_revision: int) -> bool:
    """
        Функция отправляет запрос для подтверждения контроля связи.

    Args:
        vvk_id: Идентификатор ВВК.
        user_query_interval_revision: Версия интервала запроса пользователя.

    Returns:
        bool: True, если функция выполнена успешно (статус-код 200 или 227).
        None - если нет связи.

    Raises:
        Exception: Если ответ сервера содержит статус-код, отличный от 200 или 227.
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/check'
    if DEBUG:
        url = f'http://localhost:8000/test/check'
    params = {'vvk_id': vvk_id, 'user_query_interval_revision': user_query_interval_revision}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logger_check.info("Канал связи в порядке.")
            return False
        elif response.status_code == 227:
            logger_check.info("Канал связи в порядке, но ошибка 227")
            return True
        else:
            logger_check.info("Нет соединения с АФ")
            return None
    except requests.RequestException as e:
        logger_check.error(f"Произошла ошибка при проверки состояния связи: {e}")
        return False

def request_metric(vvk_id: int) -> dict:
    """
        Функция отправляет запрос для получения метрикинфо.

    Args:
        vvk_id: Идентификатор ВВК.

    Returns:
        dict: Результат с информацией о метриках (metric_info_list, scheme_revision, user_query_interval_revision).

    Raises:
        Exception: Если ответ сервера содержит статус-код, отличный от 200.
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/metric-info-list'
    params = {'vvk_id': vvk_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            logger_check.info("Метрики от АФ получена.")
            return result
        else:
            logger_check.info("Ошибка получения метрик")
            raise Exception(f"Unexpected status code: {response.status_code}")

    except requests.RequestException as e:
        logger_check.error(f"Произошла ошибка при получении метрик: {e}")
        raise

def get_metric_info(vvk_id: int) -> bool:
    """
        При ошибке 227 запрашивает актуальные метрики и их обновляет.

     Функция выполняет следующие шаги:
     1. Запрашивает метрики для заданного VVK через функцию `request_metric`.
     2. Если запрос успешен (получены данные):
        - Обновляет таблицу `reg_sch`, вызывая функции `reg_sch_update_all_user_query_revision` и `reg_sch_update_vvk_metric_info`.
        - Обновляет таблицу `sch_ver`, вызывая функции `sch_ver_update_all_user_query_revision` и `sch_ver_update_all_metric_info`.

     Args:
         vvk_id (int): Идентификатор VVK.

     Returns:
         bool: Возвращает True, если данные были успешно получены и таблицы были обновлены.
               Возвращает False, если данные не были получены.

     Raises:
         Exception: Может вызвать исключения, если возникают ошибки при обновлении таблиц в базе данных.
     """
    temp = request_metric(vvk_id)
    # загрузить метрик инфо в таблицы
    if temp:
        # GUI
        db.gui_update_all_user_query_revision(temp["user_query_interval_revision"])
        # REG_SCH
        db.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])
        metric_info_list_dict = {
            "metric_info_list": temp["metric_info_list"]
        }
        db.reg_sch_update_vvk_metric_info(metric_info_list_dict)
        # SCH_VER
        db.sch_ver_update_all_user_query_revision(temp["user_query_interval_revision"])
        db.sch_ver_update_all_metric_info(metric_info_list_dict)

try:
    while True:
        vvk_id, _, user_query_interval_revision, t3 = db.sch_ver_select_vvk_details()

        if vvk_id:
            if227 = request_conn(vvk_id, user_query_interval_revision)
            if if227 is None:
                db.gui_update_check_number_id(vvk_id, True)
            else:
                db.gui_update_check_number_id(vvk_id, False)
                if if227:
                    get_metric_info(vvk_id)
            time.sleep(int(T3))
        else:
            print("Нет зарегистрированной VVK")
            time.sleep(60)

except Exception as e:
    disconnect(conn)
    sys.exit(1)

