from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo

from logger.logger import logger
from metric_info.service import if_metric_info

from myException import MyException427, MyException527

router = APIRouter(
    prefix="/metric-info-list",
    tags=["Metric info"]
)

@router.get("")
async def select_metric_info(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для получения 'metric_info_list'.

    Args:
        agent_id (int): Идентификатор агента, для которого требуется получить информацию о метриках.
        db (Depends): Зависимость, обеспечивающая доступ к репозиторию базы данных.

    Returns:
        dict: Словарь с ключами 'metric_info_list', 'scheme_revision' и 'user_query_interval_revision'.

    Raises:
        HTTPException: 427 или 527 с подробным сообщением об ошибке.
    """
    try:
        scheme_revision, user_query_interval_revision = db.reg_sch_select_agent_details(agent_id)
        metric_info_list = if_metric_info(db.reg_sch_select_vvk_metric_info_list())

        result = {
            "metric_info_list": metric_info_list,
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision
        }
        return result

    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})