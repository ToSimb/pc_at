import json, httpx
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from deps import get_db_repo

from config import MY_PORT

from registration.service import (
    registration_agent_reg_id_scheme,
    re_registration_agent_id_scheme,
    save_to_json,
    delete_agent
    )
from registration.schemas import AgentScheme

from myException import MyException427, MyException428, MyException429, MyException527, MyException528

from logger.logger import logger

router = APIRouter(
    prefix="/agent-scheme",
    tags=["Registration Agent"]
)


@router.post("")
def agent_scheme(agent_scheme: AgentScheme, agent_id: int = None, agent_reg_id: str = None, db=Depends(get_db_repo)):
    """
    Метод для регистрации агентов
    """
    all_agent_scheme = {
        "scheme_revision": agent_scheme.scheme_revision,
        "metric_info_list": agent_scheme.metric_info_list,
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
            raise MyException527("(RU) JoinScheme не загружена. (ENG) JoinScheme not loaded.")
        if agent_id:
            save_to_json(agent_id, "reg", all_agent_scheme)
            if agent_id in agent_ids:
                agent_reg_id_old, scheme_revision_old_agent = db.reg_sch_select_agent_details2(agent_id)
                if all_agent_scheme["scheme_revision"] > scheme_revision_old_agent:
                    # Перерегистрация
                    agent_scheme_return = re_registration_agent_id_scheme(agent_id, agent_reg_id_old, all_agent_scheme, db)
                    return agent_scheme_return
                else:
                    error_str = f"(RU) Старая версия агента '{agent_id}'. (ENG) Old version of agent '{agent_id}'."
                    db.gui_update_agent_id_error(agent_id, error_str)
                    raise MyException427(error_str)
            else:
                raise MyException428(f"(RU) Агент '{agent_id}' не зарегистрирован. (ENG) Agent_id '{agent_id}' is not registered.")
        elif agent_reg_id:
            if agent_reg_id in agents_reg_ids:
                save_to_json(agent_reg_id, "reg", all_agent_scheme)
                check_agent = db.gui_select_agent_id_for_check_agent_reg_id(agent_reg_id)
                if check_agent:
                    scheme_revision_old, _, original_scheme_old, scheme_old, response_scheme, _ = db.reg_sch_select_agent_scheme(check_agent)
                    if (all_agent_scheme["scheme"] == original_scheme_old) and (scheme_revision_old == all_agent_scheme["scheme_revision"]):
                        db.gui_update_agent_id_tru(check_agent)
                        logger.info(f"(RU) Агент '{check_agent}' вернул свой 'item_id'. (ENG) Agent '{check_agent}' successfully returned its 'item_id'.")
                        return response_scheme
                    else:
                        raise MyException428(f"(RU) Этот agent_reg_id '{agent_reg_id}' уже зарегистрирован под agent_id = '{check_agent}' и имеет версию схемы = '{scheme_revision_old}'. "
                                             f"(ENG) This agent_reg_id '{agent_reg_id}' is already registered under agent_id = '{check_agent}' and has scheme revision = '{scheme_revision_old}'.")
                else:
                    # Регистрация
                    agent_scheme_return = registration_agent_reg_id_scheme(agent_reg_id, all_agent_scheme, db)
                    return agent_scheme_return
            else:
                raise MyException429(f"(RU) В JoinScheme нет agent_reg_id = '{agent_reg_id}'. (ENG) JoinScheme does not have agent_reg_id = '{agent_reg_id}'.")
        else:
            raise MyException428("(RU) Нет ни 'agent_reg_id', ни 'agent_reg'. (ENG) There is no 'agent_reg_id' or 'agent_reg'.")

    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except KeyError as e:
        error_str = f"KeyError:(RU) Нет ключа в словаре: {e}. (ENG) Could not find the key in the dictionary: {e}."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except MyException428 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=428, detail={"error_msg": error_str})
    except MyException429 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=429, detail={"error_msg": error_str})
    except MyException527 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = (f"(RU) Vvk Scheme занят другим процессом! Попробуйте позже. "
                     f"(ENG) Vvk Scheme is busy with another process. Please try again later")
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except MyException528 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=528, detail={"error_msg": error_str})
    except ValueError as e:
        error_str = f"ValueError: {e}."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=528, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=528, detail={"error_msg": error_str})

@router.post("/upload")
async def upload_agent_scheme(file: UploadFile = File(...), agent_reg_id: str = Form(...)):
    """
    Метод для загрузки AgentScheme через файл
    """
    if file.content_type not in ["application/json", "text/json"]:
        raise HTTPException(status_code=427, detail="(RU)Файл не JSON.(ENG) JSON file is not correct")

    try:
        contents = await file.read()
        agent_all = json.loads(contents)
        if not isinstance(agent_all, dict) or "scheme_revision" not in agent_all or "scheme" not in agent_all:
            raise MyException427("(RU) Неправильное содержимое файла. (ENG) Invalid file content")

        required_fields = ["metrics", "templates", "item_id_list", "join_id_list", "item_info_list"]
        for field in required_fields:
            if field not in agent_all["scheme"]:
                raise MyException427("(RU) Неправильное содержимое файла. (ENG) Invalid file content")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{MY_PORT}/agent-scheme?agent_reg_id={agent_reg_id}",
                json=agent_all
            )

        return response.json()

    except json.JSONDecodeError:
        raise HTTPException(status_code=427, detail="(RU)Файл не JSON. (ENG) JSON file is not correct")
    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except KeyError as e:
        error_str = f"KeyError:(RU) Нет ключа в словаре {e}. (ENG) Could not find the key in the dictionary."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = f"(RU) Vvk Scheme занят другим процессом! (ENG) Vvk Scheme is busy with another process. Please try again later"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        raise HTTPException(status_code=528, detail={"error_msg": error_str})

@router.get("/delete/{agent_id}")
async def delete_agent_id(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для удаления Агента из АТ
    """
    try:
        if db.sch_ver_select_latest_status():
            return ("ВВК зарегистрирован")
        else:
            a = delete_agent(agent_id, db)
            return a
    except BlockingIOError:
        error_str = f"(RU) Vvk Scheme занят другим процессом! (ENG) Vvk Scheme is busy with another process. Please try again later"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        raise HTTPException(status_code=528, detail={"error_msg": error_str})