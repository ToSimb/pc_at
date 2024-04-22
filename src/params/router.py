from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from deps import get_db_repo
from database.database import Database

from .schemas import SchemeJson

from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH

router = APIRouter(
    prefix="/params",
    tags=["Params"]
)

"""
необывалдывдолар ывао ыр
"""
@router.post("/")
async def params_data(params: SchemeJson, vvk_id: int, db= Depends(get_db_repo)):
    print(type(params.model_dump()))
    


    for value in params.value:
        for data in value.data:
            print (params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment)
            db.execute_params(params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment)
    


    # return {"message": "OK"}
    #url_PC_AF = f"{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/{PC_AF_PATH}?vvk_id={vvk_id}"
    #return RedirectResponse(url=url_PC_AF)
    return "0k"


@router.get("/")
def hi():
    with open('myfile.txt', 'a') as f:
    # Дописываем строку в файл
        f.write('Новая строка\n')
    return ({"message": "ok"})