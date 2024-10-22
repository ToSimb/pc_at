import asyncio
import httpx
import requests
import time
import signal
import sys

from database.db import Database
from database.postgres import connect, disconnect
from logger.logger import logger

from config import MY_PORT, DEBUG, T3, PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT

def signal_handler(sig, frame):
    logger.info("Принят сигнал завершения работы. Закрытие соединения...")
    disconnect(conn)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


conn = connect()
db = Database(conn)

#______________

async def request_by_number_id(session, number_id: int):
    url = f'http://localhost:{MY_PORT}/send-packet'
    params = {'number_id': number_id}
    try:
        response = await session.get(url, params=params)
        response.raise_for_status()
        logger.info(f" @ Получен ответ для параметра '{number_id}': {response.status_code}")
    except httpx.HTTPError as e:
        logger.error(f" @ Произошла ошибка запроса для параметра '{number_id}': {str(e)}")
    except Exception as e:
        logger.error(f" @ Исключение для параметра '{number_id}': {str(e)}")

async def main_requests(number_ids):
    async with httpx.AsyncClient(timeout=httpx.Timeout(80.0, connect=15.0))as session:
        tasks = [request_by_number_id(session, number_id) for number_id in number_ids]
        await asyncio.gather(*tasks)

#______________
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

def request_registration_vvk(vvk_id: int, json_vvk_return: dict):
    """
        Отправляет запрос на регистрацию VVK.

    Args:
        vvk_id (int): Идентификатор VVK. Если идентификатор указан - то это перерегистрация,
                      иначе регистрация ВВК,
        json_vvk_return (dict): Данные в формате JSON, которые будут отправлены в запросе.

    Returns:
        dict: Ответ от сервера в формате JSON, если регистрация прошла успешно.
        None: Если произошла ошибка при выполнении запроса.

    Raises:
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    # проверка на наличие vvk_id, то есть была ли система зарегистрирована до этого или нет
    if vvk_id:
        url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme?vvk_id={vvk_id}'
        if DEBUG:
            url = f'http://localhost:{MY_PORT}/test/save?vvk_id={vvk_id}'
    else:
        url = f'{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/vvk-scheme'
        if DEBUG:
            url = f'http://localhost:{MY_PORT}/test/save'

    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            logger.info("Успешная регистрация VvkScheme на стороне АФ")
            return response.json()
        else:
            error_str = "Произошла ошибка при регистрации: " + str(response.status_code) + " : " + str(response.text)
            logger.error(error_str)
            db.gui_update_vvk_reg_error(error_str)
            return None
    except requests.RequestException as e:
        error_str = f"RequestException(Ошибка на уровне запроса): {e}."
        logger.error(error_str)
        db.gui_update_vvk_reg_error(error_str)
        return None

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
        db.reg_sch_update_all_user_query_revision(temp["user_query_interval_revision"])

        db.reg_sch_block_false()
        return True
    else:
        db.reg_sch_block_false()
        return False

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


try:
    # регистрация ВВК
    while True:
        t3 = int(T3)
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
        t3 = int(T3)
        vvk_id, _, _, t3_table = db.sch_ver_select_vvk_details()
        logger.info(" ________________________ ")
        start_time = time.time()
        if db.pf_select_has_records():
            number_ids = db.pf_select_unique_number_ids()

            loop = asyncio.get_event_loop()
            loop.run_until_complete(main_requests(number_ids))

            end_requests_time = time.time()
            logger.info(f"Для number_ids: {number_ids} общее время отправки - {end_requests_time - start_time}")
            time_1 = time.time()
            all_count_pf = db.pf_select_count_all()
            logger.info(f"Осталось данных в БД: {all_count_pf}, время запроса в БД - {time.time() - time_1}")

        else:
            if db.sch_ver_select_date_create_unreg():
                if db.gui_select_agents_check_status_reg():
                    if re_registration_vvk():
                        logger.info("Успешная перерегистрация ВВК")
                        t3 = 1
                    else:
                        logger.error("Не успешная перерегистрация ВВК.")
                else:
                    error_str = "Не все агенты успешно зарегистрированы!"
                    logger.info(error_str)
                    db.gui_update_vvk_reg_error(error_str)
            else:
                logger.info("В БД нет новых данных")

        end_time = time.time()
        time_transfer = end_time - start_time
        logger.info(f"______ВРЕМЯ ЦИКЛА__________   {time_transfer}")
        time_transfer = t3 if time_transfer > t3 else time_transfer
        time.sleep(t3 - time_transfer)

except Exception as e:
    db.reg_sch_block_false()
    error_str = str(e)
    logger.error("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)

