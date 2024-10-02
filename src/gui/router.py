from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from deps import get_db_repo

from logger.logger import logger
from gui.service import if_metric_info, open_json, get_to_json

from myException import MyException427, MyException528

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/gui",
    tags=["Gui"]
)

@router.get("", response_class=HTMLResponse)
async def gui_pages(request: Request, db=Depends(get_db_repo)):
    """
        GUI
    """
    try:
        dump = db.select_last_agents_reg("gui")
        vvk = None
        agents = None
        if dump:
            vvk = [item for item in dump if item.get("type_id") is False]
            agents = [item for item in dump if item.get("type_id") is True]
            vvk = vvk[0]
            agents.sort(key=lambda x: x.get("id"))

        return templates.TemplateResponse(
            request=request, name="main.html", context={"vvk": vvk, "agents": agents, "GLOBAL_STATUS_SAVE": db.flag_select()}
        )
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

@router.get("/upload", response_class=HTMLResponse)
async def upload_form_get(request: Request):
    """
        GUI - upload
    """
    return templates.TemplateResponse("upload_form.html", {"request": request})

@router.get("/vvk_scheme")
async def gui_pages_vvk(db=Depends(get_db_repo)):
    """
        Метод для просмотра VvkScheme
    """
    try:
        scheme_revision_vvk, user_query_interval_revision, _, vvk_scheme, _, metric_info_list = db.reg_sch_select_vvk_all()
        result = {
            "scheme_revision": scheme_revision_vvk,
            "user_query_interval_revision": user_query_interval_revision,
            "scheme": vvk_scheme,
            "metric_info_list": if_metric_info(metric_info_list)
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_params/{agent_id}")
async def gui_params_agent(agent_id: int):
    """
        Метод для просмотра последнего принято пакета Agent
    """
    try:
        file_name = f"files/pf/agent_{agent_id}.json"
        result = open_json(file_name)
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/status_save")
async def gui_status_save(db=Depends(get_db_repo)):
    """
        Метод для Вкл/Выкл статуса для сохранения последнего ПФ
    """
    try:
        logger.info("Произведена замена статуса флага")
        db.flag_update()
        return RedirectResponse("/gui")
    except Exception as e:
        return (str(e))

# _________________ Детали Агента

@router.get("/agent_details/{agent_reg_id}")
async def gui_pages_agent_details(request: Request, agent_reg_id: str, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent Details
    """
    try:
        if db.gui_select_check_agent_reg_id(agent_reg_id):
            check_agent = db.gui_select_agent_id_for_check_agent_reg_id(agent_reg_id)
            return templates.TemplateResponse(request=request, name="agent_details.html", context={"agent_reg_id": agent_reg_id, "agent_id": check_agent} )
        else:
            return ("Такого агента нет")
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_scheme_all/{agent_id}")
async def gui_pages_agent_all(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent All Scheme
    """
    try:
        scheme_revision, user_query_interval_revision, original_scheme, scheme, response_scheme = db.reg_sch_select_agent_scheme(agent_id)
        result = {
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
            "original_scheme": original_scheme,
            "scheme": scheme,
            "response_scheme": response_scheme
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_scheme/{agent_id}")
async def gui_pages_agent_scheme(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent Scheme
    """
    try:
        scheme_revision, _, _, scheme, _ = db.reg_sch_select_agent_scheme(agent_id)
        result = {
            "scheme_revision": scheme_revision,
            "scheme": scheme
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_reg_scheme/{agent_id}")
async def gui_pages_agent_reg_scheme(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent Reg Scheme
    """
    try:
        scheme_revision, _, original_scheme, _, _ = db.reg_sch_select_agent_scheme(agent_id)
        result = {
            "scheme_revision": scheme_revision,
            "scheme": original_scheme
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_save_file/{agent_id}")
async def gui_pages_agent_save_file(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent Reg Scheme (то есть - ответ на регистрацию/перерегистрацию)
    """
    try:
        result = get_to_json(agent_id, "list")
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_response/{agent_id}")
async def gui_pages_agent_response(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра Agent Response Scheme
    """
    try:
        _, _, _, _, response_scheme = db.reg_sch_select_agent_scheme(agent_id)
        return response_scheme
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_id_file/{agent_id}")
async def gui_pages_agent_id_file(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра последнего отправленного Agent Scheme при перерегистрации
    """
    try:
        result = get_to_json(agent_id, "reg")
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/agent_reg_id_file/{agent_reg_id}")
async def gui_pages_agent_reg_id_file(agent_reg_id: str, db=Depends(get_db_repo)):
    """
        Метод для просмотра последнего отправленного Agent Scheme при регистрации
    """
    try:
        result = get_to_json(agent_reg_id, "reg")
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))



# _________________ Отображение схем ВВК

@router.get("/details", response_class=HTMLResponse)
async def gui_pages_validation(request: Request, db=Depends(get_db_repo)):
    """
        GUI details
    """
    try:
        return templates.TemplateResponse( request=request, name="details.html" )
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

@router.get("/join_scheme")
async def gui_pages_join(db=Depends(get_db_repo)):
    """
        Метод для просмотра Join Scheme
    """
    try:
        scheme_revision_vvk, _, original_scheme, _, _, _ = db.reg_sch_select_vvk_all()
        result = {
            "scheme_revision": scheme_revision_vvk,
            "scheme": original_scheme,
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/all_scheme")
async def gui_pages_all_scheme(db=Depends(get_db_repo)):
    """
        Метод для просмотра AllScheme
    """
    try:
        scheme_revision_vvk, user_query_interval_revision, original_scheme, vvk_scheme, _, metric_info_list = db.reg_sch_select_vvk_all()
        result = {
            "scheme_revision": scheme_revision_vvk,
            "user_query_interval_revision": user_query_interval_revision,
            "join_scheme": original_scheme,
            "scheme": vvk_scheme,
            "metric_info_list": if_metric_info(metric_info_list)
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/vvk_scheme_true")
async def gui_pages_vvk_sch_ver_true(db=Depends(get_db_repo)):
    """
        Метод для просмотра последней успешной зарегистрированной VvkScheme
    """
    try:
        vvk_id, scheme_revision, user_query_interval_revision, status_reg, scheme, metric_info_list = db.sch_ver_select_all_vvk_if_tru()
        result = {
            "vvk_id": vvk_id,
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
            "status_reg": status_reg,
            "scheme": scheme,
            "metric_info_list": if_metric_info(metric_info_list)
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))

@router.get("/vvk_scheme_false")
async def gui_pages_vvk_sch_ver_false(db=Depends(get_db_repo)):
    """
        Метод для просмотра последней успешной зарегистрированной VvkScheme
    """
    try:
        vvk_id, scheme_revision, user_query_interval_revision, status_reg, scheme, metric_info_list = db.sch_ver_select_all_vvk_if_false()
        result = {
            "vvk_id": vvk_id,
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
            "status_reg": status_reg,
            "scheme": scheme,
            "metric_info_list": if_metric_info(metric_info_list)
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))


# __________________ Дополнительный функционал для VvkScheme

@router.get("/delete_pf")
async def gui_delete_pf_all(db=Depends(get_db_repo)):
    """
        Метод для удаления всех ПФ из БД
    """
    try:
        db.pf_delete_params()
        logger.info("ИЗ БД УДАЛЕНЫ ВСЕ ПФ")
        return RedirectResponse("/gui")
    except Exception as e:
        return (str(e))


@router.get("/block-false")
async def gui_block_false(db=Depends(get_db_repo)):
    """
        Метод для разблокировки процесса роботы с VvkScheme
    """
    try:
        db.reg_sch_block_false()
        logger.info("ПРОЦЕСС РАЗБЛОКИРОВАН")
        return RedirectResponse("/gui")
    except Exception as e:
        return (str(e))
