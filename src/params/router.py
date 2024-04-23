from fastapi import APIRouter, Depends
from deps import get_db_repo

from .schemas import SchemeJson

router = APIRouter(
    prefix="/params",
    tags=["Params"]
)

@router.post("/")
async def params_data(params: SchemeJson, vvk_id: int, db=Depends(get_db_repo)):
    for value in params.value:
        for data in value.data:
            # print(params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment)
            db.execute_params(params.scheme_revision, params.user_query_interval_revision, value.item_id, value.metric_id, data.t, data.v, data.etmax, data.etmin, data.comment)
    return "0k"


@router.get("/")
def hi():
    with open('myfile.txt', 'a') as f:
        f.write('Новая строка\n')
    return ({"message": "строка для теста записана"})