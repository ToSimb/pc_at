from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo

from logger.logger import logger

router = APIRouter(
    prefix="/check",
    tags=["Check"]
)

@router.get("")
async def get_checks(agent_id: int, user_query_interval_revision: int, db=Depends(get_db_repo)):
    """
        Метод для проверки контроля связи с агентом.

    Args:
        agent_id (int): Идентификатор агента, для которого требуется выполнить проверку.
        user_query_interval_revision (int): Ревизия интервала запросов пользователя.

    Returns:
        str: "Ok", если проверка прошла успешно и ревизии совпадают.

    Raises:
        HTTPException: Если ревизии не совпадают (статус-код 227).
        HTTPException: Если агент не зарегистрирован или произошла другая ошибка (статус-код 527).
    """
    try:
        user_q = db.reg_sch_select_agent_user_q(agent_id)
        if user_q is not None:
            db.gui_update_agent_check_number_id_tru(agent_id)
            if user_query_interval_revision == user_q:
                return Response(status_code=200)
            else:
                return Response(status_code=227)
        else:
            raise Exception(f"(RU) Агент '{agent_id}' не зарегистрирован. (ENG) Agent_id '{agent_id}' is not registered.")
    except Exception as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
