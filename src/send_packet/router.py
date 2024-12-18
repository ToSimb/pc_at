import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from deps import get_db_repo

from logger.logger_send import logger_send

from .service import (get_params_from_db_by_number_id,
                      parse_value,
                      forming_packet,
                      send_value_to_url,
                      save_to_json,)

router = APIRouter(
    prefix="/send-packet",
    tags=["Send Packet"],
)

@router.get("")
async def send_packet(number_id: int, db=Depends(get_db_repo)):
    """
        Метод для отправки пакета в АФ по agent_id/vvk_id.
    """
    try:
        start_time = time.time()
        result_id, params, len_pf = get_params_from_db_by_number_id(number_id, db)
        if params is None:
            return Response(status_code=200)
        get_time = time.time()
        value = parse_value(params)
        pars_time = time.time()
        vvk_id, result = forming_packet(value, db)
        response_code = await send_value_to_url(vvk_id, number_id, result, db)
        response_time = time.time()
        if response_code:
            if db.flag_select():
                save_to_json(result, number_id)
            save_time = time.time()
            logger_send.info(response_code)
            deleted_rows = db.pf_delete_records(result_id)
            delete_time = time.time()
            db.gui_update_value_out(vvk_id, number_id, None)
            logger_send.info("________________" + "\n"
                    + "Number_id:                 " + str(number_id) + "\n"
                    + "Количество ПФ:             " + str(len_pf) + "\n"
                    + "Время получение ПФ из БД:  " + str(get_time - start_time) + "\n"
                    + "Время формирование ПФ:     " + str(pars_time - get_time) + "\n"
                    + "Время отправки ПФ:         " + str(response_time - pars_time) + "\n"
                    + "Время сохранения ПФ:       " + str(save_time - response_time) + "\n"
                    + "Время удаления ПФ:         " + str(delete_time - save_time) + "\n"
                    + "Кол-во удаленных пакетов и первые 2 элемента :     " + str(deleted_rows) + " - " + str(result_id[:2]))
            return Response(status_code=200)
        else:
            logger_send.error(f"ОШИБКА отправки не отправлены для '{number_id}'")
            raise Exception(f"Что-то пришло другое для '{number_id}'")
    except Exception as e:
        error_str = f"{e}."
        logger_send.error(error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
