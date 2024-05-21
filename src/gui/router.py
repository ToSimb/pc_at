from fastapi import APIRouter, Depends, Request
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
    dump = db.select_last_agents_reg("gui", 20)
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

@router.get("/all_vvk_scheme")
async def all_vvk_scheme(db=Depends(get_db_repo)):
    """
    Метод для просмотра всего VvkScheme
    """
    return db.reg_sch_select_vvk_all_json()

@router.get("/gui_table")
async def gui_table(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    dump = db.select_last_agents_reg("gui", limit)
    return dump

@router.get("/reg_sch_table_all")
async def gui_table_all(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Reg_sch
    """
    dump = db.select_last_agents_reg("reg_sch", limit)
    return dump

@router.get("/reg_sch_table_no_sch")
async def reg_sch_table_no_sch(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Reg_sch
    """
    dump = db.select_last_agents_reg("reg_sch", limit)
    now_dump = [{key: value for key, value in d.items() if key not in ["scheme", "original_scheme", "metric_info_list"]} for d in dump]
    return now_dump

@router.get("/sch_ver_table")
async def sch_ver_table(limit: int = 10,db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    dump = db.select_last_agents_reg("sch_ver", limit)
    return dump

@router.get("/pf_table")
async def pf_table(limit: int = 10, db=Depends(get_db_repo)):
    """
    Метод для просмотра таблицы Gui
    """
    dump = db.select_last_agents_reg("pf", limit)
    return dump