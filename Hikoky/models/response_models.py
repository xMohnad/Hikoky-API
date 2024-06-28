2
from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    name: str
    link: str
    cover: Optional[str] = None
    badge: Optional[str] = None
    source: str

# =====================
class DataItem(BaseModel):
    name: str
    query_param: str
    base_url: str
    logo_url: str

class SourcesModel(BaseModel):
    success: bool
    data: List[DataItem]

# =============================

