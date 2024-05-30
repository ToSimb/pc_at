from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo

from logger.logger import logger
from .schemas import SchemeJson
from params.service import add_params

class MyException427(Exception):
    def __init__(self, message="427:"):
        self.message = message
        super().__init__(self.message)
class MyException227(Exception):
    def __init__(self, message="427:"):
        self.message = message
        super().__init__(self.message)

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
                scheme_revision, user_query_interval_revision, metric = db.reg_sch_select_metrics_ids(agent_id)
                if scheme_revision != params.scheme_revision:
                    raise MyException427(f"Ошибка: Agent '{agent_id}' - неверная scheme_revision, зарегестрированна: {scheme_revision}.")
                add_params(params, agent_id, metric, db)
                if user_query_interval_revision != params.user_query_interval_revision:
                    raise MyException227
                return ("OK")
            else:
                raise MyException427(
                    f"Ошибка: Agent '{agent_id}' - необходима перерегистарция.")
        else:
            raise Exception("The last scheme is not registered")

    except MyException227:
        raise HTTPException(status_code=227, detail="OK")
    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})

    except KeyError as e:
        error_str = f"KeyError: {e}. Не удалось найти ключ в словаре."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except ValueError as e:
        error_str = f"ValueError: {e}."
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}"
        db.gui_update_value(agent_id, error_str, True)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

@router.post("/hole")
async def params_hole(params: SchemeJson, vvk_id: int):
    print ("пришли ПФ от ввк:", vvk_id, params.scheme_revision)
    return ("OK")