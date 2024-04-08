from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .schemas import SchemeJson

from config import PC_AF_PROTOCOL, PC_AF_IP, PC_AF_PORT, PC_AF_PATH

router = APIRouter(
    prefix="/reception",
    tags=["Recrption"]
)


@router.post("/")
async def reception_data(data: SchemeJson):
    print(type(data.model_dump()))
    # return {"message": "OK"}
    url_PC_AF = f"{PC_AF_PROTOCOL}://{PC_AF_IP}:{PC_AF_PORT}/{PC_AF_PATH}"
    return RedirectResponse(url=url_PC_AF)


@router.post("/2/")
async def reception_data2(data: SchemeJson):
    print("++" * 10)
    return {"message": "OK"}
