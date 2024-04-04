from typing import Any

from pydantic import BaseModel


class Id_val(BaseModel):
    t: int
    v: int
    comment: str = None
    etmax: bool = None
    etmin: bool = None

class Vk_val(BaseModel):
    item_id: int
    metric_id: str
    # data: list[Id_val]
    data: list[dict[Any, Any]]

class SchemeJson(BaseModel):
    scheme_revision: int
    user_query_interval_revision: int
    value: list[Vk_val]
