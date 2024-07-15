from typing import List, Optional
from pydantic import BaseModel
from .paths import generate_manga_path, insert_manga


class SearchDetails(BaseModel):
    name: str
    link: str
    mangaPath: Optional[str] = None
    cover: Optional[str] = None
    type: Optional[str] = None
    badge: Optional[str] = None

    def save(self, source):
        manga_path = generate_manga_path(self.name)
        self.mangaPath = manga_path
        return {
            "source": source,
            "manga_path": manga_path,
            "link": self.link,
        }


class Search(BaseModel):
    source: str
    results: List[SearchDetails]

    def __init__(self, **data):
        super().__init__(**data)
        self.save_search_paths()

    def save_search_paths(self):
        if self.results:
            results = [result.save(self.source) for result in self.results]
            insert_manga(data=results)
