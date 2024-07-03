# hikoky-API/Hikoky/dependencies.py
from config import source_handlers, search_handlers
from typing import Dict, Any, Union, List, Optional

from fastapi import HTTPException
from scraper import pyparse, HttpClientError
from scraper import SearchError

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from .models.paths import PathManga, PathChapter

err = {"success": False}

# uesd in any Version
async def fetch_data(url: str, method="GET", headers=None, params=None, data=None):

    try:
        result = await pyparse(url, method, headers=headers, params=params, data=data)
        return result

    except HttpClientError as e:
        raise HTTPException(status_code=400, detail={**err, **e.detail})

async def get_handler(header_value: str):
    parsed_source_netloc = urlparse(header_value).netloc

    for handler in source_handlers:
        if parsed_source_netloc == urlparse(handler["base_url"]).netloc:
            return header_value, handler
        elif header_value.lower() == handler["name"].lower():
            return handler["base_url"], handler

    raise HTTPException(status_code=400, detail={**err, "error": "Either a valid source name or a valid URl must be provided."})
# ============================================

# About search 
async def handle_search(keyword: str, source: str) -> Union[Dict[str, Any], BeautifulSoup, str]:
    for handler in search_handlers:
        if source == handler["name"]:
            url = handler["search_URL"]
            method = handler["method"]
            headers = handler["headers"]
            params = handler.get("params")(keyword) if handler.get("params") else None
            data = handler.get("data")(keyword) if handler.get("data") else None
            name = handler["name"]

            try:
                result = await pyparse(url, method, headers, params, data)
                search_result = await handler["search"](result, name)

                return search_result

            except SearchError as e:
                raise HTTPException(status_code=404, detail=e.detail)

            except HttpClientError as e:
                raise HTTPException(status_code=400, detail={**err, **e.detail})

    raise HTTPException(status_code=400, detail={**err, "erroe": f"Invalid source, No source found {source}"})

async def handle_search_in_all_sources(keyword: str) -> List[Union[Dict[str, Any], BeautifulSoup, str]]:
    results = []

    for handler in search_handlers:
        url = handler["search_URL"]
        method = handler["method"]
        headers = handler["headers"]
        params = handler.get("params")(keyword) if handler.get("params") else None
        data = handler.get("data")(keyword) if handler.get("data") else None
        name = handler["name"]

        try:
            result = await pyparse(url, method, headers, params, data)
            search_result = await handler["search"](result, name)
            results.append(search_result)

        except SearchError as e:
            results.append(e.detail)

        except HttpClientError as e:
            results.append(e.detail)

    if not results:
        raise HTTPException(status_code=404, detail={**err, "Error": "No results found"})
    return results

# ==============================================================
# about V2

async def handle_manga_request(source: str, mangaPath: Optional[str] = None, chapterPath: Optional[str] = None) -> Dict[str, Any]:
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
    _, handler = await get_handler(source)

    if mangaPath and not chapterPath:
        link = PathManga.get_link(handler["name"], mangaPath)
        result = await fetch_data(link)
        results = handler["manga_page"](result, handler["name"], mangaPath)

    elif mangaPath and chapterPath:
        link = PathChapter.get_link(handler["name"], mangaPath, chapterPath)
        result = await fetch_data(link)
        results = handler["chapter_page"](result, link)
    else:
        pass

    return {'success': True, "source": handler["name"], "data": results}
