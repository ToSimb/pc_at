import requests
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client.database.postgres import connect, disconnect
from client.database.db import Database

conn = connect()
db = Database(conn)

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
                      иначе регистрация ВВК.
        json_vvk_return (dict): Данные в формате JSON, которые будут отправлены в запросе.

    Returns:
        dict: Ответ от сервера в формате JSON, если регистрация прошла успешно.
        None: Если произошла ошибка при выполнении запроса.

    Raises:
        requests.RequestException: Если произошла ошибка при выполнении запроса.
    """
    if vvk_id:
        url = f'http://127.0.0.1:8000/test/save?vvk_id={vvk_id}'
    else:
        url = f'http://127.0.0.1:8000/test/save'

    headers = {'Content-Type': 'application/json'}
    try:
        print(f"Отправка: {url}")
        response = requests.post(url, json=json_vvk_return, headers=headers)
        if response.status_code == 200:
            print("Успушная регистрация VvkScheme на стороне АФ")
            return response.json()
        else:
            error_str = "Произошла ошибка при регистрации: " + str(response.status_code) + " : " + str(response.text)
            print(error_str)
            db.gui_update_vvk_reg_error(error_str)
            return None
    except requests.RequestException as e:
        error_str = f"RequestException: {e}."
        print(error_str)
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
        print(error_str)
        db.gui_update_vvk_reg_error(error_str)
        return False
    db.reg_sch_block_true()
    scheme_revision, scheme, metric_info_list_raw = db.reg_sch_select_vvk_scheme()
    metric_info_list = if_metric_info(metric_info_list_raw)
    print("Извлечение метрик инфо")
    print(metric_info_list)
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

try:
    registration_vvk()

except Exception as e:
    db.reg_sch_block_false()
    error_str = str(e)
    print("Произошла ошибка: %s", error_str)
    disconnect(conn)
    sys.exit(1)
