from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo


from logger.logger import logger
from .schemas import SchemeJson
from .service import add_params, save_to_json

from myException import MyException427, MyException428, MyException527

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
        if db.sch_ver_select_latest_status():
            if db.gui_select_check_agent_status_reg(agent_id):
                scheme_revision, user_query_interval_revision, metrics, items_id = db.reg_sch_select_full_metrics_and_items_for_agent(agent_id)
                if scheme_revision != params.scheme_revision:
                    raise MyException428(f"(RU) У Агента '{agent_id}' старая схема версии = {scheme_revision}. (ENG) Agent '{agent_id}' has old scheme revision = {scheme_revision}.")
                add_params(params, agent_id, metrics, items_id, db)
                if db.flag_select():
                    save_to_json(params, agent_id)
                if user_query_interval_revision != params.user_query_interval_revision:
                    return Response(status_code=227)
                return Response(status_code=200)
            else:
                raise MyException427(
                    f"(RU) Агент '{agent_id}' не зарегистрирован. (ENG) Agent '{agent_id}' is not registered.")
        else:
            raise MyException527("(RU) VvkScheme не зарегистрирован. Попробуйте еще раз позже. "
                                 "(ENG) VvkScheme is not registered. Please try again later.")

    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except KeyError as e:
        error_str = f"KeyError:(RU) Нет ключа в словаре: {e}. (ENG) Could not find the key in the dictionary: {e}."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except MyException428 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=428, detail={"error_msg": error_str})
    except MyException527 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except ValueError as e:
        error_str = f"ValueError: {e}."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=528, detail={"error_msg": error_str})

    except Exception as e:
        error_str = f"Exception: {e}"
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=528, detail={"error_msg": error_str})
