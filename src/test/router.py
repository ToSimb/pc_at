import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo

from logger.logger import logger


router = APIRouter(
    prefix="/test",
    tags=["TEST"]
)

@router.get("/check")
async def test_get_checks(vvk_id: int, user_query_interval_revision: int):
    """
        Метод для тестовой проверки контроля связи
    """
    try:
        if vvk_id == 51:
            if user_query_interval_revision != 2:
                return Response(status_code=200)
            else:
                return Response(status_code=227)
        else:
            raise Exception("no vvk_id")
    except Exception as e:
        error_str = f"{e}."
        logger.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

@router.post("/save")
async def test_return_scheme(vvk_scheme: dict, vvk_id: int = None):
    """
    Метод для тестовой регистрации VvkScheme
    """
    return_scheme = {
        "vvk_id": 51,
        "scheme_revision": vvk_scheme["scheme_revision"],
        "user_query_interval_revision":  1
    }
    if vvk_id == 51:
        print(f"metric_info_list: {vvk_scheme['metric_info_list']}")
        return_scheme["user_query_interval_revision"] = 5
    return return_scheme

@router.get("/metric-info-list")
async def test_select_metric_info(vvk_id: int):
    """
        Метод для тестового получения 'metric_info_list'.

    """
    result = {
        "metric_info_list": [
            {
                "item_id": 13,
                "metric_id": 'cpu.user.time',
                "user_query_interval": 2
            },
            {
                "item_id": 14,
                "metric_id": 'connection.agent',
                "user_query_interval": 5
            },
            {
                "item_id": 22,
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
async def test_params_hole(params: dict, vvk_id: int):
    """
        Метод для тестового получения ПФ.

    """
    print("пришли ПФ от ввк:", vvk_id, params["scheme_revision"])
    time.sleep(2)
    return ("OK")
