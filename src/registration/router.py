from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo

from logger.logger import logger
from registration.service import create_json_vvk, add_json_vvk, reg_vvk_scheme
from registration.schemas import AgentScheme

class MyException427(Exception):
    def __init__(self, message="427:"):
        self.message = message
        super().__init__(self.message)

router = APIRouter(
    prefix="/agent-scheme",
    tags=["Registration"]
)


@router.post("/join-scheme")
def join_scheme(join_scheme: dict, db=Depends(get_db_repo)):
    """
    Метод для загрузки JionScheme
    """
    try:
        create_json_vvk(join_scheme, db)
        return ("Схема сохранена")
    except KeyError as e:
        error_str = f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail=error_str)
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail=error_str)
    except Exception as e:
        raise HTTPException(status_code=527, detail=f"Exception: {e}.")


@router.post("")
def join_scheme(agent_scheme: AgentScheme, agent_id: int = None, agent_reg_id: str = None, db=Depends(get_db_repo)):
    """
    Метод для регистрации агентов
    """
    original_agent_scheme = {
        "scheme_revision": agent_scheme.scheme_revision,
        "scheme": {
            "metrics": agent_scheme.scheme.metrics,
            "templates": agent_scheme.scheme.templates,
            "item_id_list": agent_scheme.scheme.item_id_list,
            "join_id_list": agent_scheme.scheme.join_id_list,
            "item_info_list": agent_scheme.scheme.item_info_list
        }
    }
    try:
        agent_ids, agents_reg_ids = db.gui_select_agents_reg()
        if len(agents_reg_ids) == 0:
            raise HTTPException(status_code=527, detail=f"error: Не загрежена JoinScheme.")
        if agent_id:
            if agent_id in agents_reg_ids:
                return ("метод перерегистрации еще не сделан!!")
            else:
                raise MyException427(f"Не такого '{agent_id}' agent_id в JoinScheme.")
        elif agent_reg_id:
            if agent_reg_id in agents_reg_ids:
                agent_scheme_return = add_json_vvk(original_agent_scheme, agent_reg_id, db)
                return agent_scheme_return
            else:
                raise MyException427(f"Не такого '{agent_reg_id}' agent_reg_id в JoinScheme.")
        else:
            raise MyException427("Не указаны нужные параметры для регистрации схемы агента.")
    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        raise HTTPException(status_code=427, detail=error_str)

    except KeyError as e:
        error_str = f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре."
        logger.error(error_str)
        db.gui_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail=error_str)
    except ValueError as e:
        error_str = f"Ошибка ValueError: {e}."
        logger.error(error_str)
        db.gui_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail=error_str)
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        db.gui_registration_agent(None, agent_reg_id, False, error_str)
        raise HTTPException(status_code=527, detail=error_str)
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        db.gui_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail=error_str)


@router.get("/reg-scheme")
async def return_scheme(db=Depends(get_db_repo)):
    """
    Метод для регистрации VvkSheme (пока что перенаправлен на себя)
    """
    try:
        return reg_vvk_scheme(db)
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail=error_str)
    except ValueError as e:
        error_str = f"ValueError: {e}."
        logger.error(error_str)
        return HTTPException(status_code=503, detail=error_str)
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail=error_str)


@router.post("/save")
async def return_scheme(vvk_scheme: dict):
    """
    Метод для тестовой регистрации VvkScheme
    """
    return_scheme = {
        "vvk_id": 51,
        "scheme_revision": vvk_scheme["scheme_revision"],
        "user_query_interval_revision": 0
    }
    return return_scheme
