# hikoky-API/Hikoky/dependencies/dependencies.py
from fastapi import HTTPException
from scraper import pyparse
from urllib.parse import urlparse
import importlib.util
import os
import textdistance

from .models.paths import get_link_chapter, get_link_manga
from typing import Dict, Any, Optional


err = {"success": False}


# uesd in any Version
async def list_sources():
    source_directory = "./scraper/sources"
    return [
        f.split(".")[0]
        for f in os.listdir(source_directory)
        if f.endswith(".py") and f != "__init__.py"
    ]


async def load_source(source):
    try:
        lo_source = source.strip()
        source_path = os.path.join("./scraper/sources", f"{lo_source}.py")
        spec = importlib.util.spec_from_file_location(lo_source, source_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        available_sources = await list_sources()
        suggestions = get_similar_sources(source, available_sources)

        if suggestions:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"source '{source}' not found. Did you mean: {suggestions}"
                },
                headers={"X-Suggestion": suggestions},
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={"error": f"Invalid source, No source found {source}"},
            )


def get_similar_sources(input_name, available_names):
    similarities = [
        (name, textdistance.cosine.normalized_similarity(input_name, name))
        for name in available_names
    ]
    most_similar = max(similarities, key=lambda x: x[1], default=None)
    if most_similar and most_similar[1] > 0.3:
        return most_similar[0]
    return None


async def get_module_by_url(url):
    source_netloc = urlparse(url).netloc
    sources = await list_sources()

    for s in sources:
        module = await load_source(s)
        if urlparse(module.base_url).netloc == source_netloc:
            return module

    raise HTTPException(
        status_code=404, detail={**err, "error": "A valid URL must be provided."}
    )


async def home_data(source: str):
    source = await load_source(source)
    result = await pyparse(source.base_url)

    results = await source.home(result)
    return {"success": True, "data": results}


async def more_data_home(next_page_url: str):
    source = await get_module_by_url(next_page_url)
    result = await pyparse(next_page_url)

    results = await source.home(result)
    return {"success": True, "data": results}


# ===============================================================
async def handle_manga_chapter(
    source_name: str, mangaPath: Optional[str] = None, chapterPath: Optional[str] = None
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
    source = await load_source(source_name)

    if mangaPath and not chapterPath:
        link = get_link_manga(source_name, mangaPath)
        result = await pyparse(link)
        results = await source.manga(result)
        results.save_manga_chapter_paths(mangaPath)

    elif mangaPath and chapterPath:
        link = get_link_chapter(source_name, mangaPath, chapterPath)
        result = await pyparse(link)
        results = await source.chapter(result, link)
        results.add_manga_path(mangaPath)
        results.save_chapter_paths()
    else:
        return HTTPException(
            status_code=500,
            detail={
                "success": False,
                "source": source_name,
                "error": "خطأ غير متوقع",
                "data": [],
            },
        )

    return {"success": True, "data": results}
