from fastapi import APIRouter, Depends, HTTPException, status
from deps import get_db_repo
from fastapi.responses import RedirectResponse

from logger.logger import logger
from .schemas import SchemeJson
from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH


router = APIRouter(
    prefix="/params",
    tags=["Params"]
)

@router.post("/")
async def params_data(params: SchemeJson, vvk_id: int, db=Depends(get_db_repo)):
    logger.info(f"Сохранение в бд {vvk_id}: {params.scheme_revision}: {params.user_query_interval_revision}")
    for value in params.value:
        for data in value.data:
            db.execute_params(vvk_id, params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment)
    return "0k"


@router.post("/redirect/")
async def test_data(params: SchemeJson, vvk_id: int):
    url_PC_AF = f"{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/{PC_AF_PATH}/?vvk_id={vvk_id}"
    logger.info(f"Выполнен редирект {vvk_id}: {params.scheme_revision}: {params.user_query_interval_revision}")
    return RedirectResponse(url=url_PC_AF)

@router.post("/test/")
async def test_data(params: SchemeJson, vvk_id: int):
    if params.scheme_revision == 560:
        return ("ok")
    else:
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail="error: не та версия схемы.")
