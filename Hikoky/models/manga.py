from typing import List, Optional
from dataclasses import dataclass, field,  asdict

from .search import Search
from .paths import PathManga, PathChapter, generate_manga_path


# Define a base class with the to_dict method
@dataclass
class BaseModel:
    
    def to_dict(self):
        return asdict(self)

@dataclass
class LatestChapters(BaseModel):
    latestNum: Optional[str]
    penultimateNum: Optional[str]
    latestUrl: Optional[str]
    penultimateUrl: Optional[str]

@dataclass
class MangaDetails(BaseModel):
    name: str
    link: str
    cover: str
    team: Optional[str]
    path: str = field(init=False)
    chapters: LatestChapters
    
    def __post_init__(self):
        self.path = generate_manga_path(self.name)
    
    def saver(self, source: str):
        Search(self.name, self.link, self.cover, self.team, source).save()

        PathManga(source, self.path, self.link).add_path()
        
@dataclass
class Home(BaseModel):
    mangaData: List[MangaDetails]
    nextUrl: Optional[str]

# ======================================
@dataclass
class MangaInfo(BaseModel):
    name: str 
    cover: str    
    genres: List[str]
    aboutStory: str
    totalChapters: Optional[str] = None

@dataclass
class ChapterDetails(BaseModel):
    number: str
    link: str 
    path: str = field(init=False)
    title: str
    date: str

    def __post_init__(self):
        self.path = generate_manga_path(self.number)

    def saver(self, source: str, path_chapter: str):
        PathChapter(source, path_chapter, self.number, self.link).add_path()


@dataclass
class Manga(BaseModel):
    mangaList: MangaInfo
    chapters: List[ChapterDetails]
    nextPageLink: Optional[str] = None

# ==================================================
@dataclass
class Chapter(BaseModel):
    title: str 
    imageUrls: List[str]
    nextLink: Optional[str]
    prevLink: Optional[str]

