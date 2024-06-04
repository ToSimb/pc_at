from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from deps import get_db_repo

from logger.logger import logger

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
        dump = db.select_last_agents_reg("gui", 50)
        vvk = None
        agents = None
        if dump:
            vvk = [item for item in dump if item.get("type_id") is False]
            agents = [item for item in dump if item.get("type_id") is True]
            vvk = vvk[0]
            agents.sort(key=lambda x: x.get("id"))

        return templates.TemplateResponse(
            request=request, name="item.html", context={"vvk": vvk, "agents": agents}
        )
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

@router.get("/vvk_scheme",)
async def gui_pages_vvk(db=Depends(get_db_repo)):
    """
    Метод для просмотра VvkScheme
    """
    try:
        return db.reg_sch_select_vvk_json()
    except Exception as e:
        return (str(e))

@router.get("/agent_scheme/{agent_id}",)
async def gui_pages_agent(agent_id: int, db=Depends(get_db_repo)):
    """
    Метод для просмотра AgentScheme
    """
    try:
        ans = db.reg_sch_select_agent_scheme(agent_id)
        return ans
    except Exception as e:
        return (str(e))


@router.get("/upload", response_class=HTMLResponse)
async def upload_form_get(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})




# __ ВРЕМЕННЫЕ __

@router.get("/all_vvk_scheme")
async def all_vvk_scheme(db=Depends(get_db_repo)):
    """
    Метод для просмотра всего VvkScheme
    """
    try:
        return db.reg_sch_select_vvk_all_json()
    except Exception as e:
        return (str(e))

@router.get("/gui_table")
async def gui_table(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    try:
        dump = db.select_last_agents_reg("gui", limit)
        return dump
    except Exception as e:
        return (str(e))

@router.get("/reg_sch_table_all")
async def gui_table_all(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Reg_sch
    """
    try:
        dump = db.select_last_agents_reg("reg_sch", limit)
        return dump
    except Exception as e:
        return (str(e))

@router.get("/reg_sch_table_no_sch")
async def reg_sch_table_no_sch(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Reg_sch
    """
    try:
        dump = db.select_last_agents_reg("reg_sch", limit)
        now_dump = [{key: value for key, value in d.items() if key not in ["scheme", "original_scheme", "metric_info_list"]} for d in dump]
        return now_dump
    except Exception as e:
        return (str(e))

@router.get("/sch_ver_table")
async def sch_ver_table(limit: int = 10,db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    try:
        dump = db.select_last_agents_reg("sch_ver", limit)
        return dump
    except Exception as e:
        return (str(e))

@router.get("/pf_table")
async def pf_table(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    try:
        dump = db.select_last_agents_reg("pf", limit)
        return dump
    except Exception as e:
        return (str(e))