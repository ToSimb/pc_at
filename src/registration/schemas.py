from pydantic import BaseModel
from typing import Any, List


class JoinValue(BaseModel):
    templates: List[Any]
    item_id_list: List[Any]
    item_info_list: List[Any]
    join_list: List[Any]


class JoinScheme(BaseModel):
    scheme_revision: int
    scheme: list[JoinValue]