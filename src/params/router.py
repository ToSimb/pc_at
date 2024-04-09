from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .schemas import SchemeJson

from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH

router = APIRouter(
    prefix="/params",
    tags=["Params"]
)


@router.post("/")
async def params_data(data: SchemeJson, vvk_id: int):
    print(type(data.model_dump()))
    # return {"message": "OK"}
    url_PC_AF = f"{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/{PC_AF_PATH}?vvk_id={vvk_id}"
    return RedirectResponse(url=url_PC_AF)


@router.get("/")
def hi():
    return ({"message": "ok"})