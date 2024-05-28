import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from deps import get_db_repo


from logger.logger import logger
from join_scheme.service import (
    registration_join_scheme,
    re_registration_join_scheme)

class MyException427(Exception):
    def __init__(self, message="427:"):
        self.message = message
        super().__init__(self.message)


router = APIRouter(
    prefix="/join-scheme",
    tags=["Registration Join Scheme"]
)


@router.post("")
def join_scheme(join_scheme: dict, db=Depends(get_db_repo)):
    """
    Метод для загрузки JionScheme
    """
    try:
        if db.reg_sch_select_check_vvk():
            scheme_revision_vvk, user_query_interval_revision, _, _, metric_info_list = db.reg_sch_select_vvk_all()
            if join_scheme["scheme_revision"] > scheme_revision_vvk:
                vvk_scheme_new = re_registration_join_scheme(join_scheme, user_query_interval_revision,
                                            metric_info_list, db)
                return (vvk_scheme_new)
            else:
                raise MyException427(
                    f"Ошибка: Загрезите более свежую версию JoinScheme, чем scheme_revision: {scheme_revision_vvk}.")
        else:
            vvk_scheme = registration_join_scheme(join_scheme, db)
            return (vvk_scheme)

    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})

    except KeyError as e:
        error_str = f"KeyError: {e}. Не удалось найти ключ в словаре."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        raise HTTPException(status_code=527, detail={"error_msg": error_str})


@router.post("/upload")
async def upload_json_file(file: UploadFile = File(...), db=Depends(get_db_repo)):
    """
    Метод для загрузки JionScheme через файл
    """
    if file.content_type not in ["application/json", "text/json"]:
        raise HTTPException(status_code=400, detail="Это не JSON")

    try:
        contents = await file.read()
        join_scheme = json.loads(contents)
        if not isinstance(join_scheme, dict) or "scheme_revision" not in join_scheme or "scheme" not in join_scheme:
            raise HTTPException(status_code=400, detail="Что то не так с этим JSON")


        if db.reg_sch_select_check_vvk():
            scheme_revision_vvk, user_query_interval_revision, _, _, metric_info_list = db.reg_sch_select_vvk_all()
            if join_scheme["scheme_revision"] > scheme_revision_vvk:
                vvk_scheme_new = re_registration_join_scheme(join_scheme, user_query_interval_revision,
                                            metric_info_list, db)
                return (vvk_scheme_new)
            else:
                raise MyException427(
                    f"Ошибка: Загрезите более свежую версию JoinScheme, чем scheme_revision: {scheme_revision_vvk}.")
        else:
            vvk_scheme = registration_join_scheme(join_scheme, db)
            return (vvk_scheme)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Файл JSON не корректный")
    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        raise HTTPException(status_code=427, detail={"error_msg": error_str})

    except KeyError as e:
        error_str = f"KeyError: {e}. Не удалось найти ключ в словаре."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = f"VvkScheme занят другим процессом. Повторите попытку позже"
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        raise HTTPException(status_code=527, detail={"error_msg": error_str})