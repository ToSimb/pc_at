import json
import os

from fastapi import APIRouter, Depends, HTTPException, status
from deps import get_db_repo

from logger.logger import logger
from registration.service import create_json_vvk, add_json_vvk, save_json_vvk
from registration.schemas import AgentScheme

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
        logger.error(f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=f"error: Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
    except BlockingIOError:
        logger.error(f"VvkScheme занят другим процессом. Повторите попытку позже")
        raise HTTPException(status_code=527, detail=f"VvkScheme занят другим процессом. Повторите попытку позже")
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
                error_str = f"Не такого '{agent_id}' agent_id в JoinScheme."
                logger.error(error_str)
                raise HTTPException(status_code=427, detail=error_str)
        elif agent_reg_id:
            if agent_reg_id in agents_reg_ids:
                agent_scheme_return = add_json_vvk(original_agent_scheme, agent_reg_id, db)
                return agent_scheme_return
            else:
                error_str = f"Не такого '{agent_reg_id}' agent_reg_id в JoinScheme."
                logger.error(error_str)
                raise HTTPException(status_code=427, detail=error_str)
        else:
            error_str = "Не указаны нужные параметры для регистрации схемы агента."
            logger.error(error_str)
            raise HTTPException(status_code=427, detail=error_str)
    except KeyError as e:
        error_str = f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре."
        logger.error(error_str)
        db.gut_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=error_str)
    except ValueError as e:
        error_str = f"Ошибка ValueError: {e}."
        logger.error(error_str)
        db.gut_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=error_str)
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        db.gut_registration_agent(None, agent_reg_id, False, error_str)
        raise HTTPException(status_code=527, detail=error_str)
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        db.gut_registration_agent(None, agent_reg_id, False, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail=error_str)














@router.get("/return-scheme")
async def return_scheme():
    """
    Метод для просмотра VvkScheme
    """
    try:
        with open("registration/json/vvk_scheme.json", "r") as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        logger.error("VvkScheme нет")
        return ("VvkScheme нет")


@router.get("/reg-scheme")
async def return_scheme():
    """
    Метод для регистрации VvkSheme (пока что перенаправлен на себя)
    """
    try:
        with open("registration/json/vvk_scheme.json", "r") as json_file:
            data = json.load(json_file)
            # url = f'http://192.168.123.54:25002/vvk-scheme'
            url = f'http://127.0.0.1:8000/agent-scheme/save'
            temp = save_json_vvk(url, data)
            return temp

    except ValueError as e:
        return HTTPException(status_code=503, detail=str(e))

    except FileNotFoundError:
        logger.error("VvkScheme нет")
        return ("VvkScheme нет")


@router.post("/save")
async def return_scheme(vvk_scheme: dict):
    """
    Метод для тестовой регистрации VvkScheme
    """
    with open("registration/json/save_vvk.json", 'w', encoding='utf-8') as file:
        json.dump(vvk_scheme, file, ensure_ascii=False)
    return_scheme = {
        "vvk_id": 1,
        "scheme_revision": vvk_scheme["scheme_revision"],
        "user_query_interval_revision": 0
    }
    return return_scheme


@router.get("/delete")
async def return_scheme():
    """
    Метод для удаления всех схем
    """
    for filename in os.listdir("registration/json"):
        filepath = os.path.join("registration/json", filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
    return ("Все файлы удалены")