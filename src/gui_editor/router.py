import json
from fastapi import APIRouter, Depends, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from deps import get_db_repo

from logger.logger import logger

from gui_editor.service import if_metric_info, load_new_vvk_cheme

from myException import MyException427, MyException528

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/editor",
    tags=["Editor"]
)


@router.get("", response_class=HTMLResponse)
async def editor_main(request: Request, db=Depends(get_db_repo)):
    """
        GUI EDITOR
    """
    try:
        scheme_revision, user_query_interval_revision, original_scheme, scheme, max_index, metric_info_list = db.reg_sch_select_vvk_all()
        vvk_scheme = {
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
            "scheme": scheme,
            "metric_info_list": if_metric_info(metric_info_list)
        }
        return templates.TemplateResponse(request=request, name="index.html", context={"vvk_scheme": vvk_scheme})
    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})


@router.get("/scheme")
async def editor_scheme(db=Depends(get_db_repo)):
    """
        Метод для получения Scheme
    """
    try:
        scheme_revision, user_query_interval_revision, original_scheme, scheme, max_index, metric_info_list = db.reg_sch_select_vvk_all()
        result = {
            "scheme_revision": scheme_revision,
            "user_query_interval_revision": user_query_interval_revision,
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


@router.post("/save")
async def editor_save_scheme(new_scheme_vvk: dict, db=Depends(get_db_repo)):
    """
        Метод сохранения Scheme с редактора
    """
    try:
        required_fields = ["scheme_revision", "scheme", "metric_info_list"]
        for field in required_fields:
            if field not in new_scheme_vvk:
                raise MyException427("(RU) Неправильное содержимое файла. (ENG) Invalid file content")
        required_fields2 = ["metrics", "templates", "item_id_list", "item_info_list"]
        for field in required_fields2:
            if field not in new_scheme_vvk["scheme"]:
                raise MyException427("(RU) Неправильное содержимое файла. (ENG) Invalid file content")
        load_new_vvk_cheme(new_scheme_vvk, db)
        return "Успешная загрузка."

    except MyException427 as e:
        error_str = f"{e}."
        logger.error(error_str)
        return error_str
        # raise HTTPException(status_code=427, detail={f"{error_str}"})
    except BlockingIOError:
        error_str = f"(RU) Vvk Scheme занят другим процессом! (ENG) Vvk Scheme is busy with another process. Please try again later."
        logger.error(error_str)
        return error_str
        # raise HTTPException(status_code=527, detail={f"{error_str}"})
    except Exception as e:
        error_str = f"Exception: {e}."
        return error_str
        # raise HTTPException(status_code=528, detail={f"{error_str}"})