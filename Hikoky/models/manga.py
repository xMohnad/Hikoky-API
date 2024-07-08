from .search import Search
from .paths import PathManga, PathChapter, generate_manga_path
from pydantic import BaseModel
from typing import List, Optional


class LatestChapters(BaseModel):
    num: Optional[str]
    url: Optional[str]
    path: Optional[str] = None

    def saver(self, source: str, manga_name: str):
        manga_path = generate_manga_path(manga_name)
        PathChapter(source, manga_path, self.num, self.url).add_path()
        self.path = f"/v2/source/{source}/{manga_path}/{self.num}"


class MangaDetails(BaseModel):
    name: str
    link: str
    cover: str
    path: str = None
    team: Optional[str]
    latestChapters: List[LatestChapters]

    def saver(self, source: str):
        path = generate_manga_path(self.name)
        Search(self.name, self.link, self.cover, self.team, source).save()
        PathManga(source, path, self.link).add_path()
        self.path = f"/v2/source/{source}/{path}"


class Home(BaseModel):
    mangaData: List[MangaDetails]
    nextUrl: Optional[str]


# ======================================
class MangaInfo(BaseModel):
    name: str
    cover: str
    genres: List[str]
    aboutStory: str
    totalChapters: Optional[str] = None


class ChapterDetails(BaseModel):
    number: str
    link: str
    path: Optional[str] = None
    title: str
    date: str

    def saver(self, source: str, manga_path: str):
        if self.number:
            PathChapter(source, manga_path, self.number, self.link).add_path()
            self.path = f"/v2/source/{source}/{manga_path}/{self.number}"


class Manga(BaseModel):
    mangaList: MangaInfo
    chapters: List[ChapterDetails]
    nextPageLink: Optional[str] = None


# ==================================================


class NavigationLink(BaseModel):
    chapterUrl: Optional[str] = None
    path: Optional[str] = None

    def saver(self, source: str, manga_path: str, number: Optional[str]):
        if number and self.chapterUrl:
            PathChapter(source, manga_path, number, self.chapterUrl).add_path()
            self.path = f"/v2/source/{source}/{manga_path}/{number}"


class Chapter(BaseModel):
    title: str
    imageUrls: List[str]
    nextNavigation: Optional[NavigationLink] = None
    prevNavigation: Optional[NavigationLink] = None
