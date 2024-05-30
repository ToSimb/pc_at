from pydantic import BaseModel
from typing import Any, List, Optional


class AgentSchemeValue(BaseModel):
    metrics: List[Any]
    templates: List[Any]
    item_id_list: List[Any]
    join_id_list: Optional[List[Any]] = None
    item_info_list: List[Any]


class AgentScheme(BaseModel):
    scheme_revision: int
    scheme: AgentSchemeValue
    metric_info_list: Optional[List[Any]] = None
