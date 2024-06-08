from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from deps import get_db_repo

from logger.logger import logger
from gui.service import if_metric_info

from myException import MyException427

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

@router.get("/upload", response_class=HTMLResponse)
async def upload_form_get(request: Request):
    """
        GUI - upload
    """
    return templates.TemplateResponse("upload_form.html", {"request": request})

@router.get("/vvk_scheme",)
async def gui_pages_vvk(db=Depends(get_db_repo)):
    """
        Метод для просмотра VvkScheme
    """
    try:
        scheme_revision_vvk, user_query_interval_revision, _, vvk_scheme, metric_info_list = db.reg_sch_select_vvk_all()
        result = {
            "scheme_revision_vvk": scheme_revision_vvk,
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

@router.get("/agent_scheme/{agent_id}",)
async def gui_pages_agent(agent_id: int, db=Depends(get_db_repo)):
    """
        Метод для просмотра AgentScheme
    """
    try:
        scheme_revision, user_query_interval_revision, scheme = db.reg_sch_select_agent_scheme(agent_id)
        result = {
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
            "scheme": scheme
        }
        return result
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        return (str(e))


