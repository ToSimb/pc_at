import json

from myException import MyException528

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

def open_json(agent_id, suffix):
    try:
        file_name = f"files/{suffix}/agent_{agent_id}.json"
        with open(file_name, 'r', encoding='utf-8') as file:
            data = file.read()
        return json.loads(data)
    except FileNotFoundError:
        raise MyException528(f"(RU) Файл с agent_id '{agent_id}' не найден. (ENG) File with agent_id '{agent_id}' not found")

def get_to_json(agent_id, suffix) -> dict:
    try:
        filename = f"files/{suffix}/agent_{agent_id}.json"
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read()
        return json.loads(data)
    except FileNotFoundError:
        raise MyException528(f"(RU) Файл с agent_id '{agent_id}' не найден. (ENG) File with agent_id '{agent_id}' not found")
