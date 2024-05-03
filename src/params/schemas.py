from pydantic import BaseModel

class Data(BaseModel):
    t: int
    v: str
    comment: str = None
    etmax: bool = None
    etmin: bool = None


class Value(BaseModel):
    item_id: int
    metric_id: str
    data: list[Data]


class SchemeJson(BaseModel):
    scheme_revision: int
    user_query_interval_revision: int
    value: list[Value]
