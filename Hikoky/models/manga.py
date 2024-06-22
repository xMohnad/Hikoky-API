from typing import List, Optional
from dataclasses import dataclass, asdict
from .search import Search

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
    chapters: LatestChapters
    team: Optional[str] = None
    
    def saver(self, source: Optional[str] = None):
        Search(self.name, self.link, self.cover, self.team, source).save()

@dataclass
class Home(BaseModel):
    mangaData: List[MangaDetails]
    nextUrl: Optional[str]

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
    title: str
    date: str

@dataclass
class Manga(BaseModel):
    mangaList: MangaInfo
    chapters: List[ChapterDetails]
    nextPageLink: Optional[str] = None

@dataclass
class Chapter(BaseModel):
    title: str 
    imageUrls: List[str]
    nextLink: Optional[str]
    prevLink: Optional[str]

