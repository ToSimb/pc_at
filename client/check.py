import requests
import time
import signal
import sys
import json

from database.db import Database
from database.postgres import connect, disconnect
from logger.logger_check import logger_check

from config import MY_PORT, PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, T3, DEBUG

TEMPLATES_ID = "agent_connection"
METRIC_ID = "connection.agent"

def signal_handler(sig, frame):
    logger_check.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

conn = connect()
db = Database(conn)

time_counter = 1
mil_with_agent_metrics = []

def if_metric_info(metric_info: dict) -> list:
    if metric_info is None:
        return []

    metric_info_list = metric_info.get('metric_info_list')

    if not metric_info_list or metric_info_list == [None]:
        return []

    return metric_info_list

def filter_by_metric_id(data, target_metric_id):
    return [item for item in data if item['metric_id'] == target_metric_id]

def save_to_json(data):
    filename = f"mil.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def time_change(ans):
    if ans is None:
        return 0
    timestamp_float = ans.timestamp()
    timestamp_int = int(timestamp_float)
    return timestamp_int

def request_conn(vvk_id: int, user_query_interval_revision: int) -> bool:
    """
        Функция отправляет запрос для подтверждения контроля связи.

    Args:
        vvk_id: Идентификатор ВВК,
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
        url = f'http://localhost:{MY_PORT}/test/check'
    params = {'vvk_id': vvk_id, 'user_query_interval_revision': user_query_interval_revision+1}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            logger_check.info("Канал связи в порядке.")
            return False
        elif response.status_code == 227:
            logger_check.info("Канал связи в порядке, но ошибка 227 - необходимо обновить metric_info")
            return True
        else:
            logger_check.info("Нет соединения с АФ")
            return None
    except requests.RequestException as e:
        logger_check.error(f"Произошла ошибка при проверки состояния связи: {e}")
        return None

def request_metric(vvk_id: int) -> dict:
    """
        Функция отправляет запрос для получения метрикинфо (metric_info).

    Args:
        vvk_id: Идентификатор ВВК.

    Returns:
        dict: Результат с информацией о метриках (metric_info_list, scheme_revision, user_query_interval_revision).

    Raises:
        Exception: Если ответ сервера содержит статус-код, отличный от 200.
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/metric-info-list'
    if DEBUG:
        url = f'http://localhost:{MY_PORT}/test/metric-info-list'
    params = {'vvk_id': vvk_id}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            result = response.json()
            logger_check.info("Метрики от АФ получены.")
            return result
        else:
            logger_check.info("Ошибка получения метрик от АФ")
            raise Exception(f"(RU) Ошибка запроса. (ENG) Unexpected status code: {response.status_code}")

    except requests.RequestException as e:
        logger_check.error(f"Произошла ошибка при получении метрик от АФ: {e}")
        raise

def get_metric_info(vvk_id: int, vvk_scheme_revision: int) -> bool:
    """
        При ошибке 227 запрашивает актуальные метрики и их обновляет.

     Args:
         vvk_id (int): Идентификатор ВВК,
         vvk_scheme_revision (int): Версия схемы ВВК.

     Returns:
         bool: Возвращает True, если данные были успешно получены и таблицы были обновлены.
               Возвращает False, если данные не были получены.

     Raises:
         Exception: Может вызвать исключения, если возникают ошибки при обновлении таблиц в базе данных.
     """
    temp = request_metric(vvk_id)
    # загрузить метрик инфо в таблицы
    if temp:
        # Проверка на совпадения версии схем - но отключена
        if vvk_scheme_revision != temp['scheme_revision']:
            logger_check.error(f"Не совпадают версии схем при обновлении Metric_info")

        metric_info_list_dict = {
            "metric_info_list": temp["metric_info_list"]
        }
        # GUI
        db.gui_update_all_user_query_revision(temp["user_query_interval_revision"])
        # REG_SCH
        db.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])
        db.reg_sch_update_vvk_metric_info(metric_info_list_dict)
        # SCH_VER
        db.sch_ver_update_all_user_query_revision(temp["user_query_interval_revision"])
        db.sch_ver_update_all_metric_info(metric_info_list_dict)
        # mil_with_agent_metrics
        global mil_with_agent_metrics
        mil_with_agent_metrics = filter_by_metric_id(temp["metric_info_list"], METRIC_ID)
        save_to_json(mil_with_agent_metrics)

def get_user_query_interval(mil, item_id):
    for item in mil:
        if item['item_id'] == item_id:
            return item['user_query_interval']
    return None


try:
    while True:
        logger_check.info("____________________________")
        start_time = time.time()
        logger_check.info(int(start_time))
        vvk_id, vvk_scheme_revision, user_query_interval_revision, t3, metric_info_list_raw = db.sch_ver_select_vvk_details_all()
        mil = if_metric_info(metric_info_list_raw)
        mil_with_agent_metrics = filter_by_metric_id(mil, METRIC_ID)
        save_to_json(mil_with_agent_metrics)

        if vvk_id:
            if227 = request_conn(vvk_id, user_query_interval_revision)
            if if227 is None:
                db.gui_update_vvk_check_number_id_false(vvk_id)
            else:
                db.gui_update_vvk_check_number_id_tru(vvk_id)
                if if227:
                    get_metric_info(vvk_id, vvk_scheme_revision)

            time_counter += 1

            if db.sch_ver_select_latest_status():
                query_interval_all = db.reg_sch_select_query_intervals_all(METRIC_ID)
                # проверка, что метрика для контроля связи есть
                if query_interval_all is not None:
                    value = []
                    agents = db.gui_select_agents_details()
                    for agent in agents:
                        # Проверка, что агент зарегистрирован
                        if agent[0] is not None:
                            late_time = max(time_change(agent[1]), time_change(agent[2]))
                            status = True
                            # если не было ответа от агента больше 10 секунд - ERROR
                            if int(start_time) - late_time > 10:
                                status = False
                                db.gui_update_agent_check_number_id_false(agent[0])
                            item_ids = db.reg_sch_select_item_ids(agent[0], TEMPLATES_ID)
                            if status:
                                logger_check.info(f"Агент '{agent[0]}' - OK")
                            else:
                                logger_check.info(f"Агент '{agent[0]}' - нет связи!")
                            # проверка, что есть пути с контролем связи
                            if item_ids is not None:
                                for item_id in item_ids:
                                    # проверка, что метрика для контроля связи есть
                                    result = None
                                    # Проверка Метрик Инфо !
                                    query_interval = query_interval_all
                                    ans = get_user_query_interval(mil_with_agent_metrics, item_id)
                                    if ans is not None:
                                        query_interval = ans
                                    if query_interval != 0:
                                        if time_counter % query_interval == 0:
                                            result = {
                                                'item_id': item_id,
                                                'metric_id': METRIC_ID,
                                            }
                                            if status:
                                                data_item = {
                                                    't': int(start_time),
                                                    'v': "OK"
                                                }
                                            else:
                                                comment_error = f"Нет связи с Агентом: {agent[0]}"
                                                data_item = {
                                                    't': int(start_time),
                                                    'v': "FATAL",
                                                    'comment': comment_error
                                                }
                                            result.update(data_item)
                                        if result is not None:
                                            value.append(result)
                    logger_check.info(f"Количество собранных метрик в цикле: {len(value)}")
                    if len(value) > 0:
                        items_id = []
                        for agent in value:
                            items_id.append(agent["item_id"])
                        logger_check.info(f"Список метрик: {items_id}")
                        db.pf_insert_params_of_1_packet(0, len(value), value)
                else:
                    logger_check.error(f"Нет метрики: {METRIC_ID}")

            end_time = time.time()
            total_time = end_time - start_time
            adjusted_total_time = min(total_time, 1)
            logger_check.debug(f"Затраченное время: {adjusted_total_time}")
            time.sleep(1 - adjusted_total_time)
        else:
            logger_check.info("Нет зарегистрированной VVK")
            time.sleep(60)

except Exception as e:
    disconnect(conn)
    sys.exit(1)

