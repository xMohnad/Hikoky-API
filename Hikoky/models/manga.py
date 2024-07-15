from .paths import generate_manga_path
from pydantic import BaseModel
from typing import List, Optional
from Hikoky.models.paths import insert_chapter, insert_manga


class LatestChapters(BaseModel):
    number: Optional[str]
    url: str
    mangaPath: Optional[str] = None
    chapterPath: Optional[str] = None

    def save(self, source: str, manga_name: str):
        self.mangaPath = generate_manga_path(manga_name)
        self.chapterPath = self.number
        return {
            "source": source,
            "manga_path": self.mangaPath,
            "chapter_num": self.number,
            "link": self.url,
        }


class MangaDetails(BaseModel):
    name: str
    link: str
    mangaPath: Optional[str] = None
    cover: str
    team: Optional[str] = None
    latestChapters: List[LatestChapters]

    def save(self, source: str):
        self.mangaPath = generate_manga_path(self.name)
        path = generate_manga_path(self.name)
        return {
            "source": source,
            "manga_path": path,
            "link": self.link,
        }


class Home(BaseModel):
    source: Optional[str]
    mangaData: List[MangaDetails]
    nextUrl: Optional[str] = None

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
    chapterPath: Optional[str] = None
    title: str
    date: str

    def save(self, source: str, manga_path: str):
        self.chapterPath = self.number
        if self.number and manga_path:
            return {
                "source": source,
                "manga_path": manga_path,
                "chapter_num": self.number,
                "link": self.link,
            }


class Manga(BaseModel):
    source: Optional[str]
    mangaPath: Optional[str] = None
    mangaList: MangaInfo
    chapters: List[ChapterDetails]
    nextPageLink: Optional[str] = None

    def save_manga_chapter_paths(self, manga_path: str):
        if manga_path:
            self.mangaPath = manga_path
            print(manga_path)
            chapter_paths = [
                chapter.save(self.source, manga_path) for chapter in self.chapters
            ]
            insert_chapter(chapter_paths)


# ==================================================
class NavigationLink(BaseModel):
    chapterUrl: Optional[str] = None
    chapterPath: Optional[str] = None

    def save(self, source: str, manga_path: str):
        if self.chapterPath and self.chapterUrl and manga_path:
            return {
                "source": source,
                "manga_path": manga_path,
                "chapter_num": self.chapterPath,
                "link": self.chapterUrl,
            }


class Chapter(BaseModel):
    source: Optional[str]
    mangaPath: Optional[str] = None
    title: str
    imageUrls: List[str]
    nextNavigation: Optional[NavigationLink] = None
    prevNavigation: Optional[NavigationLink] = None

    def add_manga_path(self, manga_path: str):
        self.mangaPath = manga_path

    def save_chapter_paths(self):
        paths = []
        if self.mangaPath and self.nextNavigation:
            paths.append(
                self.nextNavigation.save(source=self.source, manga_path=self.mangaPath)
            )
        if self.mangaPath and self.prevNavigation:
            paths.append(
                self.prevNavigation.save(source=self.source, manga_path=self.mangaPath)
            )
        insert_chapter(data=paths)
