from .search import Search

# import os
# import pkgutil
# import importlib

# package_dir = os.path.dirname(__file__)

# for _, module_name, _ in pkgutil.iter_modules([package_dir]):
#     module = importlib.import_module(f".{module_name}", package=__name__)
#     for attribute_name in dir(module):
#         if not attribute_name.startswith("_"):
#             globals()[attribute_name] = getattr(module, attribute_name)


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

from .response_models import SourcesModel, SearchResult

__all__ = [
    "MangaDetails",
    "LatestChapters",
    "MangaInfo",
    "ChapterDetails",
    "Search",
    "Home",
    "Manga",
    "Chapter",
    "NavigationLink",
    "SourcesModel",
    "SearchResult",
]
