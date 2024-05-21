import time

from logger.logger import logger
from .schemas import SchemeJson


def add_params(params, agent_id: int, metric: list, db) -> bool:
    start_time = time.time()
    pf = []
    for value in params.value:
        for data in value.data:
            if value.metric_id in metric:
                pf.append((value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment))
            else:
                raise ValueError(f"Метрики {value.metric_id} нет в схеме!!")
    db.pf_insert_params(pf)
    end_time = time.time()
    execution_time = end_time - start_time
    db.gui_update_value(agent_id, None, True)
    logger.info(f"Сохранение в бд ({agent_id}:{params.scheme_revision}:{params.user_query_interval_revision}) "
                f"count: {len(pf)} time: {execution_time}")
