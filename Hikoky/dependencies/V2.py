from fastapi import HTTPException
from Hikoky.dependencies.dependencies import fetch_data, get_handler_source
from ..models.paths import PathManga, PathChapter

from typing import Dict, Any, Optional


async def handle_manga_chapter(
    source: str, mangaPath: Optional[str] = None, chapterPath: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handles the manga request based on the provided source, manga path, and chapter path.

    Args:
    - source (str): The source name.
    - mangaPath (Optional[str]): The path to the manga. Default is None.
    - chapterPath (Optional[str]): The path to the chapter. Default is None.

    Returns:
    - Dict[str, Any]: A dictionary with the success status, source name, and the requested data.

    Raises:
    - HTTPException
    """
    handler = await get_handler_source(source)

    source = handler["name"]

    if mangaPath and not chapterPath:
        link = PathManga.get_link(source, mangaPath)
        result = await fetch_data(link)
        results = handler["manga_page"](result, source, mangaPath)

    elif mangaPath and chapterPath:
        link = PathChapter.get_link(source, mangaPath, chapterPath)
        result = await fetch_data(link)
        results = handler["chapter_page"](result, link, source, mangaPath)
    else:
        return HTTPException(
            status_code=500,
            detail={
                "success": False,
                "source": source,
                "error": "خطأ غير متوقع",
                "data": [],
            },
        )

    return {"success": True, "source": handler["name"], "data": results}
