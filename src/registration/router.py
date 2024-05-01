import json
import os

from fastapi import APIRouter, HTTPException, status

from logger.logger import logger
from registration.service import create_json_vvk, add_json_vvk, save_json_vvk

from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH
from .schemas import JoinScheme

router = APIRouter(
    prefix="/agent-scheme",
    tags=["Registration"]
)


@router.post("/join-scheme")
def join_scheme(json_join_scheme: dict):
    """
    Метод для звгрузки JionScheme
    """
    try:
        create_json_vvk(json_join_scheme)
        return ("Схема сохранена")
    except KeyError as e:
        logger.error(f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=f"error: Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
    except FileNotFoundError as e:
        logger.error(f"Ошибка FileNotFoundError: {e}. Не удалось найти или открыть файл.")
        raise HTTPException(status_code=527, detail=f"error: Ошибка FileNotFoundError: {e}. Не удалось найти или открыть файл.")
    except BlockingIOError as e:
        logger.error(f"Файл занят другим процессом. Повторите попытку позже. {e}")
        raise HTTPException(status_code=527, detail=f"error: Файл занят другим процессом. Повторите попытку позже. {e}")
    except IOError as e:
        logger.error(f"Файл занят другим процессом. Повторите попытку позже. {e}")
        raise HTTPException(status_code=527, detail=f"error: Файл занят другим процессом. Повторите попытку позже. {e}")

@router.post("/")
def join_scheme(json_agent_scheme: dict, agent_reg_id: str = None, agent_id: int = None):
    """
    Метод для регистрации агентов
    """
    try:
        if agent_reg_id:
            agent_scheme_return = add_json_vvk(json_agent_scheme, agent_reg_id)
            return agent_scheme_return
        elif agent_id:
            print("Переригистрация")
        else:
            logger.error("Не указаны нужные параметры для регистрации схемы агента.")
            raise HTTPException(status_code=427, detail=f"error: Не указаны нужные параметры.")
    except KeyError as e:
        logger.error(f"Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=f"error: Ошибка KeyError: {e}. Не удалось найти ключ в словаре.")
    except ValueError as e:
        logger.error(f"Ошибка ValueError: {e}.")
        raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=f"error: Ошибка ValueError: {e}.")
    except FileNotFoundError as e:
        logger.error(f"Ошибка FileNotFoundError: {e}. Не удалось найти или открыть файл.")
        raise HTTPException(status_code=527, detail=f"error: Ошибка FileNotFoundError: {e}. Не удалось найти или открыть файл.")
    except BlockingIOError as e:
        logger.error(f"Файл занят другим процессом. Повторите попытку позже. {e}")
        raise HTTPException(status_code=527, detail=f"error: Файл занят другим процессом. Повторите попытку позже. {e}")
    except IOError as e:
        logger.error(f"Файл занят другим процессом. Повторите попытку позже. {e}")
        raise HTTPException(status_code=527, detail=f"error: Файл занят другим процессом. Повторите попытку позже. {e}")

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