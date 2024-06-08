import requests
import time
import signal
import sys

from database.db import Database
from database.postgres import connect, disconnect
from logger.logger import logger

def signal_handler(sig, frame):
    logger.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

INT_LIMIT = 30000
T3 = 5

conn = connect()
db = Database(conn)

# !!!
def if_metric_info(metric_info: dict) -> list:
    """
    Возвращает 'metric_info_list' из словаря metric_info, если оно существует.

    Args:
        metric_info (dict): Словарь, содержащий ключ 'metric_info_list', значение которого будет проверено.

    Returns:
        list: Список, содержащий значение по ключу 'metric_info_list', или пустой список, если значение отсутствует или некорректно.
    """
    if metric_info is None:
        return []

    metric_info_list = metric_info.get('metric_info_list')

    if not metric_info_list or metric_info_list == [None]:
        return []

    return metric_info_list

# !!!
def request_pf(final_result: dict, vvk_id: int) -> bool:
    """
        Функция отправляет ПФ на сервер с помощью HTTP POST запроса.

    Args:
        final_result: Словарь с данными, которые нужно отправить на сервер.
        vvk_id: Идентификатор, который включается в URL запроса.

    Returns:
        bool: True, если функция выполнена успешно (статус-код 200 или 227).

    Raises:
        Exception: Если ответ сервера содержит статус-код, отличный от 200 или 227.
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/params?vvk_id={vvk_id}'
    url = f'http://localhost:8000/params/hole?vvk_id={vvk_id}'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=final_result, headers=headers)
        if response.status_code == 200:
            logger.info("Данные успешно отправлены.")
            return True
        elif response.status_code == 227:
            logger.info("Данные отправлены, но ошибка 227")
            return True
        else:
            error_str = "Произошла ошибка при отправке данных:" + str(response.status_code) + " : " + str(response.text)
            raise Exception(error_str)
    except requests.RequestException as e:
        logger.error(f"Произошла ошибка при отправке данных: {e}")
        return False

# !!!
def request_registration_vvk(vvk_id: int, json_vvk_return: dict):
    """
        Отправляет запрос на регистрацию VVK.

    Args:
        vvk_id (int): Идентификатор VVK. Если идентификатор указан - то это перерегистрация,
                      иначе регистрация ВВК.
        json_vvk_return (dict): Данные в формате JSON, которые будут отправлены в запросе.

    Returns:
        dict: Ответ от сервера в формате JSON, если регистрация прошла успешно.
        None: Если произошла ошибка при выполнении запроса.

    Raises:
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    if vvk_id:
        # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme?vvk_id={vvk_id}'
        url = f'http://127.0.0.1:8000/join-scheme/save?vvk_id={vvk_id}'
    else:
        # url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme'
        url = f'http://127.0.0.1:8000/join-scheme/save'

    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            logger.info("Успушная регистрация VvkScheme на стороне АФ")
            return response.json()
        else:
            error_str = "Произошла ошибка при регистрации: " + str(response.status_code) + " : " + str(response.text)
            logger.error(error_str)
            db.gui_update_vvk_reg_error(error_str)
            return None
    except requests.RequestException as e:
        error_str = f"RequestException: {e}."
        logger.error(error_str)
        db.gui_update_vvk_reg_error(error_str)
        return None

# !!!
def parse_value(params: list) -> tuple:
    """
        Парсит и собирает ПФ по item_id и metric_id.

    Args:
        params (list): Список ПФ из таблицы, содержащих параметры.

    Returns:
        tuple: Список идентификаторов ПФ из таблицы (result_id) и Value для отправки (output_data).
    """
    result = {}
    result_id =[]
    for item in params:
        result_id.append(item['id'])
        item_id = item['item_id']
        metric_id = item['metric_id']
        t = item['t']
        v = item['v']
        comment = item.get('comment')
        etmax = item.get('etmax')
        etmin = item.get('etmin')

        key = (item_id, metric_id)

        if key not in result:
            result[(item_id, metric_id)] = {
                'item_id': item_id,
                'metric_id': metric_id,
                'data': []
            }

        data_item = {
            't': t,
            'v': v
        }
        if comment is not None:
            data_item['comment'] = comment
        if etmax is not None:
            data_item['etmax'] = etmax
        if etmin is not None:
            data_item['etmin'] = etmin

        result[key]['data'].append(data_item)

    output_data = sorted(result.values(), key=lambda x: (x['item_id'], x['metric_id']))

    return result_id, output_data

# !!!
def registration_vvk() -> bool:
    """
        Регистрирует VVK в системе.

    Returns:
        bool: Возвращает True, если регистрация выполнена успешно, иначе False.
    """
    # REG_SCH
    if db.reg_sch_block_check():
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.info(error_str)
        db.gui_update_vvk_reg_error(error_str)
        return False
    db.reg_sch_block_true()
    scheme_revision, scheme, metric_info_list_raw = db.reg_sch_select_vvk_scheme()
    metric_info_list = if_metric_info(metric_info_list_raw)
    data = {
        "scheme_revision": scheme_revision,
        "scheme": scheme,
        "metric_info_list": metric_info_list
    }
    temp = request_registration_vvk(None, data)
    if temp:
        # GUI
        db.gui_update_vvk_reg_true(temp["vvk_id"], temp["scheme_revision"], temp["user_query_interval_revision"])

        metric_info_list_dict = {
            "metric_info_list": metric_info_list
        }
        # SCH_VER
        db.sch_ver_insert_vvk(True, temp["vvk_id"], temp["scheme_revision"],
                                  temp["user_query_interval_revision"], scheme, metric_info_list_dict)

        # REG_SCH
        db.reg_sch_update_vvk_id(temp["vvk_id"])

        db.reg_sch_block_false()
        return True
    else:
        db.reg_sch_block_false()
        return False

# !!!
def re_registration_vvk() -> bool:
    """
        Перерегистрирует VVK в системе.

    Returns:
        bool: Возвращает True, если перерегистрация выполнена успешно, иначе False.
    """
    # REG_SCH
    if db.reg_sch_block_check():
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.info(error_str)
        db.gui_update_vvk_reg_error(error_str)
        return False
    db.reg_sch_block_true()

    vvk_id, scheme_revision, scheme, metric_info_list_raw = db.sch_ver_select_vvk_details_unreg()
    metric_info_list = if_metric_info(metric_info_list_raw)
    data = {
        "scheme_revision": scheme_revision,
        "scheme": scheme,
        "metric_info_list": metric_info_list
    }
    temp = request_registration_vvk(vvk_id, data)
    if temp:
        # GUI
        db.gui_update_vvk_reg_true(temp["vvk_id"], temp["scheme_revision"], temp["user_query_interval_revision"])

        # SCH_VER
        db.sch_ver_update_all_user_query_revision(temp["user_query_interval_revision"])
        db.sch_ver_update_status_reg(temp["scheme_revision"])

        # REG_SCH
        db.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])

        db.reg_sch_block_false()
        return True
    else:
        db.reg_sch_block_false()
        return False


vvk_id = None # Необходима для исколючения

try:
    # регистрация ВВК
    while True:
        t3 = T3
        vvk_id, _, _, _ = db.sch_ver_select_vvk_details()
        if vvk_id:
            logger.info("Есть зарегистрированная VVkScheme")
            break
        agent_ids, agents_reg_ids = db.gui_select_agents_reg()
        if agents_reg_ids == []:
            logger.info("Загрузите JoinSCheme")
        else:
            if len(agent_ids) != len(agents_reg_ids):
                error_str = "Не все агенты зарегистрированы!"
                logger.info(error_str)
                db.gui_update_vvk_reg_error(error_str)
            else:
                if db.gui_select_agents_check_status_reg():
                    if registration_vvk():
                        break
                else:
                    error_str = "Не все агенты успешно зарегистрированы!"
                    logger.info(error_str)
                    db.gui_update_vvk_reg_error(error_str)

        time.sleep(t3)

    # передача ПФ
    while True:
        t3 = T3
        start_time = time.time()
        date_create = db.sch_ver_select_date_create_unreg()
        if date_create:
            params = db.pf_select_params_json_unreg(date_create, INT_LIMIT)
        else:
            params = db.pf_select_params_json(INT_LIMIT)
        if len(params) > 0:
            result_id, value = parse_value(params)
            vvk_id, scheme_revision, user_query_interval_revision, t3 = db.sch_ver_select_vvk_details()
            t3 = t3 if t3 is not None else T3
            result = {
                "scheme_revision": scheme_revision,
                "user_query_interval_revision": user_query_interval_revision,
                "value": value
            }
            start_request_time = time.time()
            if request_pf(result, vvk_id):
                updated_rows = db.pf_update_sent_status(result_id)
                db.gui_update_value(vvk_id, None, False)
                count_sent_false = db.pf_select_count_sent_false()
                logger.info("DB(pf): изменено строк (true): %d | ОСТАЛОСЬ в БД: %d", updated_rows, count_sent_false)
                if count_sent_false > INT_LIMIT:
                    t3 = 0
            end_request_time = time.time()
            logger.info("Время формирование ПФ: %.4f | время отправки: %.4f", start_request_time-start_time, end_request_time-start_request_time)
        else:
            if date_create:
                if db.gui_select_agents_check_status_reg():
                    if re_registration_vvk():
                        logger.info("Успешная перегистрация ВВК")
                        t3 = 5
                    else:
                        logger.error("Не успешная перегистрация ВВК.")
                else:
                    error_str = "Не все агенты успешно зарегистрированы!"
                    logger.info(error_str)
                    db.gui_update_vvk_reg_error(error_str)
            else:
                logger.info("В БД нет новых данных")

        end_time = time.time()
        time_transfer = end_time - start_time
        time_transfer = t3 if time_transfer > t3 else time_transfer

        time.sleep(t3 - time_transfer)

except Exception as e:
    db.reg_sch_block_false()
    error_str = str(e)
    logger.error("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)

