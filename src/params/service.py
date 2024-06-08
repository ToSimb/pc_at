import time

from logger.logger import logger

from database.database import Database
from myException import MyException427

# !!!
def add_params(params, agent_id: int, metrics_id: list, items_id: list, db: Database) -> bool:
    """
        Добавляет параметры в базу данных.

    Args:
        params: Объект, содержащий значения и данные для добавления.
        agent_id: Идентификатор агента.
        metrics_id: Список допустимых метрик.
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
    for value in params.value:
        if value.metric_id in metrics_id:
            if str(value.item_id) in items_id:
                for data in value.data:
                    pf.append((value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment))
            else:
                raise MyException427(f"Item_id '{value.item_id}' is not in the scheme!")
        else:
            raise MyException427(f"Metric '{value.metric_id}' is not in the scheme!")
    db.pf_insert_params(pf)
    end_time = time.time()
    execution_time = end_time - start_time
    db.gui_update_value(agent_id, None, True)
    logger.info(f"Сохранение в бд ({agent_id}:{params.scheme_revision}:{params.user_query_interval_revision}) "
                f"count: {len(pf)} time: {execution_time}")
    return True
