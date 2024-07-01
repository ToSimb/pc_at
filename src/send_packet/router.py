import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo

from logger.logger_send import logger_send

from .service import (get_params_from_db_by_number_id,
                      parse_value,
                      forming_packet,
                      send_value_to_url,)

router = APIRouter(
    prefix="/send-packet",
    tags=["Send Packet"],
)

@router.get("")
async def send_packet(number_id: int, db=Depends(get_db_repo)):
    """
        Метод для отправки пакета в АТ по agent_id/vvk_id.
    """
    try:
        start_time = time.time()
        result_id, params = get_params_from_db_by_number_id(number_id, db)
        if params is None:
            return Response(status_code=227)
        get_time = time.time()
        value = parse_value(params)
        pars_time = time.time()
        vvk_id, result = forming_packet(value, db)
        response_code = await send_value_to_url(vvk_id, result)
        response_time = time.time()
        if response_code in {200, 227}:
            db.pf_delete_records(result_id)
        delete_time = time.time()
        logger_send.info("________________" + "\n"
                    + "Number_id:                 " + str(number_id) + "\n"
                    + "Время получение ПФ из БД:  " + str(get_time - start_time) + "\n"
                    + "Время формирование ПФ:     " + str(pars_time - get_time) + "\n"
                    + "Время отправки ПФ:         " + str(response_time - pars_time) + "\n"
                    + "Время удаления ПФ:         " + str(delete_time - response_time))
        return Response(status_code=response_code)

    except Exception as e:
        error_str = f"{e}."
        logger_send.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})