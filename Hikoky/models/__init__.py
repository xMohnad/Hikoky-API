from .search import Search

from .manga import (
    # Home page for displaying manga for the source
    Home,
    MangaDetails,
    LatestChapters,
    # Manga display page for the source
    Manga,
    MangaInfo,
    ChapterDetails,
    # Chapter presentation page
    Chapter,
    NavigationLink,
)

__all__ = [
    "Home",
    "MangaDetails",
    "LatestChapters",
    "Manga",
    "MangaInfo",
    "ChapterDetails",
    "Chapter",
    "NavigationLink",
    "Search",
]
