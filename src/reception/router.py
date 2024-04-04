from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .schemas import SchemeJson


router = APIRouter(
    prefix="/reception",
    tags=["Recrption"]
)


@router.post("/")
async def reception_data(data: SchemeJson):
    print(type(data.model_dump()))
    # return {"message": "OK"}
    return RedirectResponse(url="http://127.0.0.1:8000/reception/2/")


@router.post("/2/")
async def reception_data2(data: SchemeJson):
    print("++" * 10)
    return {"message": "OK"}
