import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from deps import get_db_repo

from logger.logger import logger
from join_scheme.service import (
    registration_join_scheme,
    re_registration_join_scheme,)

from myException import MyException427


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
            scheme_revision_vvk, user_query_interval_revision, _, vvk_scheme, max_index, metric_info_list_raw = db.reg_sch_select_vvk_all()
            if join_scheme["scheme_revision"] > scheme_revision_vvk:
                vvk_scheme_new = re_registration_join_scheme(join_scheme, user_query_interval_revision,
                                            metric_info_list_raw, vvk_scheme, max_index, db)
                return (vvk_scheme_new)
            else:
                raise MyException427(
                    f"(RU)Загрузите более свежую версию, чем '{scheme_revision_vvk}'! (ENG) Download a newer version.")
        else:
            vvk_scheme = registration_join_scheme(join_scheme, db)
            return (vvk_scheme)

    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except KeyError as e:
        error_str = f"KeyError:(RU) Нет ключа в словаре: {e}. (ENG) Could not find the key in the dictionary."
        logger.error(error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = (f"(RU) Vvk Scheme занят другим процессом! Попробуйте позже. "
                     f"(ENG) Vvk Scheme is busy with another process. Please try again later")
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        db.reg_sch_block_false()
        raise HTTPException(status_code=528, detail={"error_msg": error_str})


@router.post("/upload")
async def upload_json_file(file: UploadFile = File(...), db=Depends(get_db_repo)):
    """
    Метод для загрузки JoinScheme через файл
    """
    if file.content_type not in ["application/json", "text/json"]:
        raise HTTPException(status_code=427, detail="(RU)Файл не JSON.(ENG) JSON file is not correct")

    try:
        contents = await file.read()
        join_scheme = json.loads(contents)
        if not isinstance(join_scheme, dict) or "scheme_revision" not in join_scheme or "scheme" not in join_scheme:
            raise MyException427("(RU) Неправильное содержимое файла. (ENG) Invalid file content")

        if db.reg_sch_select_check_vvk():
            scheme_revision_vvk, user_query_interval_revision, _, vvk_scheme, max_index, metric_info_list_raw = db.reg_sch_select_vvk_all()
            if join_scheme["scheme_revision"] > scheme_revision_vvk:
                vvk_scheme_new = re_registration_join_scheme(join_scheme, user_query_interval_revision,
                                            metric_info_list_raw, vvk_scheme, max_index, db)
                return (vvk_scheme_new)
            else:
                raise MyException427(
                    f"(RU) Загрузите более свежую версию, чем {scheme_revision_vvk}! (ENG) Download a newer version.")
        else:
            vvk_scheme = registration_join_scheme(join_scheme, db)
            return (vvk_scheme)

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

