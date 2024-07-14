from .paths import generate_manga_path
from pydantic import BaseModel
from typing import List, Optional
from Hikoky.models.paths import insert_chapter, insert_manga


class LatestChapters(BaseModel):
    num: Optional[str]
    url: Optional[str]
    path: Optional[str] = None

    def save(self, source: str, manga_name: str):
        manga_path = generate_manga_path(manga_name)
        self.path = f"/v2/source/{source}/{manga_path}/{self.num}"
        return {
            "source": source,
            "manga_path": manga_path,
            "chapter_num": self.num,
            "link": self.url,
        }


class MangaDetails(BaseModel):
    name: str
    link: str
    cover: str
    path: str = None
    team: Optional[str] = None
    latestChapters: List[LatestChapters]

    def save(self, source: str):
        path = generate_manga_path(self.name)
        self.path = f"/v2/source/{source}/{path}"
        return {
            "source": source,
            "manga_path": path,
            "link": self.link,
        }


class Home(BaseModel):
    source: Optional[str]
    mangaData: List[MangaDetails]
    nextUrl: Optional[str]

    def __init__(self, **data):
        super().__init__(**data)
        self.save_home_paths(self.source, self.mangaData)

    def save_home_paths(self, source: str, mangas: List[MangaDetails]):
        manga_paths = [manga.save(source) for manga in mangas]
        chapter_paths = [
            chapter.save(source, manga.name)
            for manga in mangas
            for chapter in manga.latestChapters
        ]
        insert_manga(manga_paths)
        insert_chapter(chapter_paths)


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

    def save(self, source: str, manga_path: str):
        if self.number and manga_path:
            self.path = f"/v2/source/{source}/{manga_path}/{self.number}"
            return {
                "source": source,
                "manga_path": manga_path,
                "chapter_num": self.number,
                "link": self.link,
            }


class Manga(BaseModel):
    source: Optional[str]
    mangaList: MangaInfo
    chapters: List[ChapterDetails]
    nextPageLink: Optional[str] = None


# ==================================================
class NavigationLink(BaseModel):
    chapterNum: Optional[str] = None
    chapterUrl: Optional[str] = None
    path: Optional[str] = None
    _path_seve: Optional[dict] = None

    def save(self, source: str, manga_path: str, number: Optional[str]):
        if number and self.chapterUrl and manga_path:
            self.path = f"/v2/source/{source}/{manga_path}/{number}"
            self._path_seve = {
                "source": source,
                "manga_path": manga_path,
                "chapter_num": number,
                "link": self.chapterUrl,
            }


class Chapter(BaseModel):
    source: Optional[str]
    title: str
    imageUrls: List[str]
    nextNavigation: Optional[NavigationLink] = None
    prevNavigation: Optional[NavigationLink] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.save_chapter_paths()

    def save_chapter_paths(self):
        paths = []
        if self.nextNavigation and self.nextNavigation._path_seve:
            paths.append(self.nextNavigation._path_seve)
        if self.prevNavigation and self.prevNavigation._path_seve:
            paths.append(self.prevNavigation._path_seve)
        insert_chapter(data=paths)
