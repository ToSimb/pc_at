from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo

from logger.logger import logger
from .schemas import SchemeJson
from params.service import add_params, file_save

from myException import MyException427, MyException527, GLOBAL_STATUS_SAVE


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
                scheme_revision, user_query_interval_revision, metrics, items_id = db.reg_sch_select_metrics_and_items(agent_id)
                if scheme_revision != params.scheme_revision:
                    raise MyException427(f"Agent '{agent_id}' - invalid scheme_revision, registered: {scheme_revision}.")
                add_params(params, agent_id, metrics, items_id, db)
                if GLOBAL_STATUS_SAVE:
                    file_save(agent_id, params)
                if user_query_interval_revision != params.user_query_interval_revision:
                    return Response(status_code=227)
                return Response(status_code=200)
            else:
                raise MyException527(
                    f"Agent '{agent_id}' - re-registration required.")
        else:
            raise Exception("The latest VVK scheme is not registered")

    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except MyException527 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

    except ValueError as e:
        error_str = f"ValueError: {e}."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except KeyError as e:
        error_str = f"KeyError: {e}. Could not find the key in the dictionary."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}"
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
