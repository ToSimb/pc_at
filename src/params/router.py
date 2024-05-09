import time

from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo

from logger.logger import logger
from .schemas import SchemeJson


router = APIRouter(
    prefix="/params",
    tags=["Params"]
)

@router.post("")
async def params_data(params: SchemeJson, agent_id: int, db=Depends(get_db_repo)):
    """
    Метод для получения ПФ и сохранения в БД
    """
    try:
        start_time = time.time()
        pf = []
        for value in params.value:
            for data in value.data:
                pf.append((value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment))
        db.pf_executemany_params(pf)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Сохранение в бд ({agent_id}:{params.scheme_revision}:{params.user_query_interval_revision}) "
                    f"count: {len(pf)} time: {execution_time} ")
        return ("0k")
    except Exception as e:
        raise HTTPException(status_code=527, detail=f"error: Произошла ошибка при выполнении запроса: {e}")

