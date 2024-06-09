from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo

from logger.logger import logger

from myException import MyException227

router = APIRouter(
    prefix="/test",
    tags=["TEST"]
)

@router.get("/check")
async def test_get_checks(vvk_id: int, user_query_interval_revision: int, db=Depends(get_db_repo)):
    """
        Метод для тестовой проверки контроля связи
    """
    try:
        if vvk_id == 51:
            if user_query_interval_revision != 2:
                return ("ok")
            else:
                raise MyException227
        else:
            raise Exception("no vvk_id")
    except MyException227:
        raise HTTPException(status_code=227, detail="OK")
    except Exception as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})


@router.post("/save")
async def test_return_scheme(vvk_scheme: dict):
    """
    Метод для тестовой регистрации VvkScheme
    """
    print(vvk_scheme)
    return_scheme = {
        "vvk_id": 51,
        "scheme_revision": vvk_scheme["scheme_revision"],
        "user_query_interval_revision":  0
    }
    return return_scheme

@router.get("/metric-info-list")
async def test_select_metric_info(vvk_id: int):
    """
        Метод для тестового получения 'metric_info_list'.

    """
    result = {
        "metric_info_list": [
            {
                "item_id": 12,
                "metric_id": 'cpu.user.time',
                "user_query_interval": 2
            },
            {
                "item_id": 21,
                "metric_id": 'cpu.user.time',
                "user_query_interval": 2
            },
            {
                "item_id": 24,
                "metric_id": 'cpu.user.time',
                "user_query_interval": 2
            },
        ],
        "scheme_revision": 0,
        "user_query_interval_revision": 5
    }
    return result

@router.post("/params")
async def params_hole(params: dict, vvk_id: int):
    """
        Метод для тестового получения ПФ.

    """
    print("пришли ПФ от ввк:", vvk_id, params["scheme_revision"])
    return ("OK")