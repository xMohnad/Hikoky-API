from fastapi import APIRouter, Query
from ..dependencies import get_handler, fetch_data

from ..models.paths import PathManga

router = APIRouter()

async def hand(source, mangaPath, chapterPath=None):
    _, handler = await get_handler(source)

    if mangaPath and chapterPath is None:
        link = PathManga.get_link(handler["name"], mangaPath)
        result = await fetch_data(link)
        results = handler["manga_page"](result)



    return results


@router.get("/{source}/{mangaPath}", tags=["Manga"])
async def read_manga_path(source: str, mangaPath: str):

    return await hand(source, mangaPath)

