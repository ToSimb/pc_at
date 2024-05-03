from fastapi import APIRouter, Depends, HTTPException, status
from deps import get_db_repo
from fastapi.responses import RedirectResponse

from logger.logger import logger
from .schemas import SchemeJson
from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH

import time

router = APIRouter(
    prefix="/params",
    tags=["Params"]
)

@router.post("")
async def params_data(params: SchemeJson, vvk_id: int, db=Depends(get_db_repo)):
    """
    Метод для получения ПФ и сохранения в БД
    """
    start_time = time.time()
    pf = []
    for value in params.value:
        for data in value.data:
            pf.append((vvk_id, params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment))
    db.pf_execute_params(pf)
    end_time = time.time()
    execution_time = end_time - start_time

    logger.info(f"Сохранение в бд {vvk_id}: {params.scheme_revision}: {params.user_query_interval_revision} time: {execution_time} count: {len(pf)}")
    return "0k"


@router.post("/redirect/")
async def test_data(params: SchemeJson, vvk_id: int):
    """
    Метод для перенаправки данных в ПС АФ
    """
    url_PC_AF = f"{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/{PC_AF_PATH}/?vvk_id={vvk_id}"
    logger.info(f"Выполнен редирект {vvk_id}: {params.scheme_revision}: {params.user_query_interval_revision}")
    return RedirectResponse(url=url_PC_AF)

