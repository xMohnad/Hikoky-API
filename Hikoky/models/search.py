from typing import List, Optional
from pydantic import BaseModel
from .paths import generate_manga_path, insert_manga


class SearchDetails(BaseModel):
    name: str
    link: str
    path: Optional[str] = None
    cover: Optional[str] = None
    type: Optional[str] = None
    badge: Optional[str] = None
    _path_seve: Optional[dict] = None

    def save(self, source):
        manga_path = generate_manga_path(self.name)
        self.path = f"/v2/source/{source}/{manga_path}"
        self._path_seve = {
            "source": source,
            "manga_path": manga_path,
            "link": self.link,
        }


class Search(BaseModel):
    source: str
    result: List[SearchDetails]

    def __init__(self, **data):
        super().__init__(**data)
        self.save_search_paths()

    def save_search_paths(self):
        results = []
        if self.result:
            for manga in self.result:
                results.append(manga._path_seve)
            insert_manga(data=results)
