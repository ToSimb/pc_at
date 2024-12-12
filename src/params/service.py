import time
import json

from .schemas import SchemeJson

from logger.logger import logger

from config import DEBUG

from database.database import Database
from myException import MyException427, MyException428


def save_to_json(params, agent_id):
    logger.info(f"Saving params agent '{agent_id}' to json")
    model_dict = params.dict()
    with open(f"files/pf/agent_{agent_id}.json", 'w', encoding='utf-8') as json_file:
        json.dump(model_dict, json_file, ensure_ascii=False, indent=4)

def add_params(params: SchemeJson, agent_id: int, metrics: list, items_id: list, db: Database) -> bool:
    """
        Добавляет параметры в базу данных.

    Args:
        params: Объект, содержащий значения и данные для добавления.
        agent_id: Идентификатор агента.
        metrics: Список допустимых метрик.
        items_id: Список допустимых идентификаторов объектов.
        db: Объект базы данных с методами для вставки и обновления данных.

    Returns:
        bool: True, если функция выполнена успешно.

    Raises:
        ValueError: Если метрика из params отсутствует в списке metrics_id.
        ValueError: Если идентификатор объекта из params отсутствует в списке items_id.
    """
    start_time = time.time()
    pf = []
    len_pf = 0
    if DEBUG:
        # metrics_id = ['chassis.uptime',
        #               'cpu.user.time',
        #               'cpu.core.load',
        #               'chassis.memory.total',
        #               'chassis.memory.used',
        #               'сompboard.voltage',
        #               'сompboard.power',
        #               'сompboard.state']
        items_id_no_str = list(range(12, 18))
        items_id = [str(item) for item in items_id_no_str]
    for value in params.value:
        found = False
        for metric in metrics:
            if value.metric_id == metric["metric_id"]:
                found = True
                if str(value.item_id) in items_id:
                    for data in value.data:
                        if data.t > start_time:
                            raise MyException428("(RU) Неправильное время опроса PF. (ENG) Incorrect PF polling time.")
                        if metric["type"] == "double":
                            try:
                                if not (-1.7976931348623157e+308 <= float(data.v) <= 1.7976931348623157e+308):
                                    raise MyException427(
                                    f"(RU) Metric_id '{value.metric_id}', Item_id {value.item_id} пареметр не double. (ENG) Metric_id '{value.metric_id}', Item_id {value.item_id} parameter not double.")

                            except Exception as e:
                                raise MyException427(f"Metric_id '{value.metric_id}', Item_id {value.item_id} - {e}.")
                        if metric["type"] == "integer":
                            try:
                                if not (-2 ** 63 <= int(data.v) <= 2 ** 63 - 1):
                                    raise MyException427(
                                        f"(RU) Metric_id '{value.metric_id}', Item_id {value.item_id} пареметр не int. (ENG) Metric_id '{value.metric_id}', Item_id {value.item_id} parameter not integer.")
                            except Exception as e:
                                raise MyException427(f"Metric_id '{value.metric_id}', Item_id {value.item_id} - {e}.")
                        len_pf += 1
                        element = {
                            'item_id': value.item_id,
                            'metric_id': value.metric_id,
                            't': data.t,
                            'v': data.v,
                            'etmax': data.etmax,
                            'etmin': data.etmin,
                            'comment': data.comment
                        }
                        # print(element)
                        filtered_element = {k: v for k, v in element.items() if v is not None}
                        pf.append(filtered_element)
                else:
                    raise MyException427(
                        f"(RU) Item_id '{value.item_id}' отсутствует в схеме. (ENG) Item_id '{value.item_id}' is not in the scheme.")

        if not found:
            raise MyException427(
                f"(RU) Metric_id '{value.metric_id}' отсутствует в схеме. (ENG) Metric_id '{value.metric_id}' is not in the scheme.")

    db.pf_insert_params_of_1_packet(agent_id, len_pf, pf)
    end_time = time.time()
    execution_time = end_time - start_time
    db.gui_update_value(agent_id, None, True)
    logger.info(f"Сохранение в бд ({agent_id}:{params.scheme_revision}:{params.user_query_interval_revision}) "
                f"count: {len(pf)} time: {execution_time}")
    return True
